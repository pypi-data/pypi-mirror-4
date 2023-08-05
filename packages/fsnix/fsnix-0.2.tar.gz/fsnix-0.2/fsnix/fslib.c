/*************************************************************************
 * fsnxi/fslib.c : posix *at and other file system functions
 *
 * Exposes posix functions like openat, unlinkat and such to
 * python. These newer posix functions are not exposed by
 * the python standard library in python 2.x.
 *
 * 
 * Copyright (c) 2011, 2012 Nasuni Corporation  http://www.nasuni.com/
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included
 * in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 * OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 *
 */


#include <Python.h>
#include <structseq.h>

/* hack to compile both on linux and freebsd;
   on freebsd python's header is restricting me 
   to 200112L, but I need 2008 for O_CLOEXEC. Also
   the python devs yell at anyone who wants to customize
   this by setting something before Python.h is included
*/
#if _POSIX_C_SOURCE < 200809
#undef __POSIX_VISIBLE
#define __POSIX_VISIBLE 200809
#endif

#include <fcntl.h>
#include <dirent.h>

#define MODULE_NAME "fslib"

/* define MAXPATHLEN like python's posix module */
#ifndef MAXPATHLEN
#if defined(PATH_MAX) && PATH_MAX > 1024
#define MAXPATHLEN PATH_MAX
#else
#define MAXPATHLEN 1024
#endif
#endif

/* internal flags */
#define INCL_DTYPE 1

/* force values to HAVE_UTIMENSAT to 0/1 */
#ifdef HAVE_UTIMENSAT
#define HAVE_UTIMENSAT 1
#else
#define HAVE_UTIMENSAT 0
#endif


static PyObject * bail_like_posix(char * name)
{
    PyObject *rc = PyErr_SetFromErrnoWithFilename(PyExc_OSError, name);
    PyMem_Free(name);
    return rc;
}

PyDoc_STRVAR(fslib_openat__doc__,
"openat(dirfd, pathname [, flags] [, mode=0600]) -> int\n\n"
"Opens a file descriptor in the same manner as os.open, but\n"
"takes an initial file descriptor argument. If pathname is\n"
"relative then the path will be relative to the directory\n"
"referred to by the dirfd."
);

static PyObject * fslib_openat(PyObject *self, PyObject *args)
{
    int dirfd;
    int fd;
    char * path = NULL;
    int flags = 0;
    mode_t mode = 0600;

    if (!PyArg_ParseTuple(args, "iet|ii:openat",
                          &dirfd,
                          Py_FileSystemDefaultEncoding, &path,
                          &flags, &mode)) {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    fd = openat(dirfd, path, flags, mode);
    Py_END_ALLOW_THREADS

    if (fd < 0) {
        return bail_like_posix(path);
    }
    PyMem_Free(path);
    return PyInt_FromLong((long)fd);
}


PyDoc_STRVAR(fslib_unlinkat__doc__,
"unlinkat(dirfd, pathname [, flags]) -> None\n\n"
"Unlinks a file in a manner similar to os.unlink, but\n"
"takes an initial file descriptor argument. If pathname is\n"
"relative then the path will be relative to the directory\n"
"referred to by the dirfd.\n"
"If the flags argument contains the AT_REMOVEDIR flag, then\n"
"unlink at removes directories instead of files."
);

static PyObject * fslib_unlinkat(PyObject *self, PyObject *args)
{
    int dirfd;
    char * path = NULL;
    int flags = 0;
    int sts = 0;

    if (!PyArg_ParseTuple(args, "iet|i:unlinkat",
                          &dirfd,
                          Py_FileSystemDefaultEncoding, &path,
                          &flags)) {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    sts = unlinkat(dirfd, path, flags);
    Py_END_ALLOW_THREADS

    if (sts != 0) {
        return bail_like_posix(path);
    }
    PyMem_Free(path);
    Py_RETURN_NONE;
}


PyDoc_STRVAR(fslib_mkfifoat__doc__,
"mkfifoat(dfd, pathname [, mode=0666])\n\n"
"Creates a FIFO (named pipe) like os.mkfifo().\n"
"If pathname is relative then the FIFO is created relative to\n"
"the directory referred to by the directory file descriptor dfd."
);

static PyObject * fslib_mkfifoat(PyObject *self, PyObject *args)
{
    int dirfd;
    char * path = NULL;
    mode_t mode = 0666;
    int sts;

    if (!PyArg_ParseTuple(args, "iet|i:mkfifoat",
                          &dirfd,
                          Py_FileSystemDefaultEncoding, &path,
                          &mode)) {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    sts = mkfifoat(dirfd, path, mode);
    Py_END_ALLOW_THREADS

    if (sts != 0) {
        return bail_like_posix(path);
    }
    PyMem_Free(path);
    Py_RETURN_NONE;
}


PyDoc_STRVAR(fslib_mkdirat__doc__,
"mkdirat(dirfd, pathname [, mode=0777])\n\n"
"Create a directory, like os.mkdir.\n"
"If pathname is relative then the file is created relative to\n"
"the directory referred to by the directory file descriptor dfd.\n"
);

static PyObject * fslib_mkdirat(PyObject *self, PyObject *args)
{
    int dirfd;
    char * path = NULL;
    mode_t mode = 0777;
    int sts;

    if (!PyArg_ParseTuple(args, "iet|i:mkdirat",
                          &dirfd,
                          Py_FileSystemDefaultEncoding, &path,
                          &mode)) {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    sts = mkdirat(dirfd, path, mode);
    Py_END_ALLOW_THREADS

    if (sts != 0) {
        return bail_like_posix(path);
    }
    PyMem_Free(path);
    Py_RETURN_NONE;
}


PyDoc_STRVAR(fslib_mknodat__doc__,
"mknodat(dirfd, pathname [, mode=0600, device])\n\n"
"Create a filesystem node, like os.mknod.\n"
"If pathname is relative then the file is created relative to\n"
"the directory referred to by the directory file descriptor dfd.\n"
"See the docs for os.mknod for details about the mode and device args.\n"
);

static PyObject * fslib_mknodat(PyObject *self, PyObject *args)
{
    int dirfd;
    char * path = NULL;
    mode_t mode = 0600;
    dev_t device = 0;
    int sts;

    if (!PyArg_ParseTuple(args, "iet|ii:mknodat",
                          &dirfd,
                          Py_FileSystemDefaultEncoding, &path,
                          &mode, &device)) {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    sts = mknodat(dirfd, path, mode, device);
    Py_END_ALLOW_THREADS

    if (sts != 0) {
        return bail_like_posix(path);
    }
    PyMem_Free(path);
    Py_RETURN_NONE;
}


PyDoc_STRVAR(fslib_fchownat__doc__,
"fchownat(dirfd, pathname, uid, gid, [, flags])\n\n"
"Change the user and group ownership of a file, like os.chown.\n"
"The uid and gid parameters must be integers.\n"
"If pathname is relative then the file is modified relative to\n"
"the directory referred to by the directory file descriptor dfd.\n"
"Specifying the AT_SYMLINK_NOFOLLOW flag will cause the function\n"
"to operate on symlinks rather than the file it points to.\n"
);

static PyObject * fslib_fchownat(PyObject *self, PyObject *args)
{
    int dirfd;
    char * path = NULL;
    int flags = 0;
    long uid = -1;
    long gid = -1;
    int sts;

    if (!PyArg_ParseTuple(args, "ietll|i:fchownat",
                          &dirfd,
                          Py_FileSystemDefaultEncoding, &path,
                          &uid, &gid, &flags)) {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    sts = fchownat(dirfd, path, (uid_t)uid, (gid_t)gid, flags);
    Py_END_ALLOW_THREADS

    if (sts != 0) {
        return bail_like_posix(path);
    }
    PyMem_Free(path);
    Py_RETURN_NONE;
}


PyDoc_STRVAR(fslib_fchmodat__doc__,
"fchmodat(dirfd, pathname, mode, [, flags])\n\n"
"Change the access permissions of a file, like os.chmod.\n"
"If pathname is relative then the file is modified relative to\n"
"the directory referred to by the directory file descriptor dfd.\n"
"Specifying the AT_SYMLINK_NOFOLLOW flag will cause the function\n"
"to operate on symlinks rather than the file it points to.\n"
);

static PyObject * fslib_fchmodat(PyObject *self, PyObject *args)
{
    int dirfd;
    char * path = NULL;
    mode_t mode = 0;
    int flags = 0;
    int sts;

    if (!PyArg_ParseTuple(args, "ieti|i:fchmodat",
                          &dirfd,
                          Py_FileSystemDefaultEncoding, &path,
                          &mode, &flags)) {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    sts = fchmodat(dirfd, path, mode, flags);
    Py_END_ALLOW_THREADS

    if (sts != 0) {
        return bail_like_posix(path);
    }
    PyMem_Free(path);
    Py_RETURN_NONE;
}


PyDoc_STRVAR(fslib_faccessat__doc__,
"faccessat(dirfd, pathname, mode) -> bool\n\n"
"Test for access permissions in the same manner as os.access.\n"
"If pathname is relative then the file is created relative to\n"
"the directory referred to by the directory file descriptor dfd.\n"
"Currently, there is no mechanism to get the errno.\n"
);

static PyObject * fslib_faccessat(PyObject *self, PyObject *args)
{
    int dirfd;
    char * path = NULL;
    mode_t mode = 0;
    int flags = 0;
    int sts;

    if (!PyArg_ParseTuple(args, "ieti|i:faccessat",
                          &dirfd,
                          Py_FileSystemDefaultEncoding, &path,
                          &mode, &flags)) {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    sts = faccessat(dirfd, path, mode, flags);
    Py_END_ALLOW_THREADS

    PyMem_Free(path);
    return PyBool_FromLong(sts == 0);
}


PyDoc_STRVAR(fslib_readlinkat__doc__,
"readlinkat(dirfd, pathname) -> path\n\n"
"Read the path a symlink points to, like os.readlink.\n"
"If pathname is relative then the symlink is accessed relative to\n"
"the directory referred to by the directory file descriptor dfd.\n"
);

static PyObject * fslib_readlinkat(PyObject *self, PyObject *args)
{
    PyObject *linkpath;
    char buf[MAXPATHLEN];
    int dirfd;
    char * path = NULL;
    int sts;

    if (!PyArg_ParseTuple(args, "iet:readlinkat",
                          &dirfd,
                          Py_FileSystemDefaultEncoding, &path)) {
        return NULL;
    }

    /* Note: Not implementing Unicode output for now, for
     * simplicity. In the future we can copy what os.readlink does.
     */

    Py_BEGIN_ALLOW_THREADS
    sts = readlinkat(dirfd, path, buf, sizeof(buf));
    Py_END_ALLOW_THREADS

    if (sts < 0) {
        return bail_like_posix(path);
    }
    linkpath = PyString_FromStringAndSize(buf, sts);
    PyMem_Free(path);
    return linkpath;
}


PyDoc_STRVAR(fslib_symlinkat__doc__,
"symlinkat(src, dirfd, pathname)\n\n"
"Create a symlink pointing to src, like os.symlink.\n"
"If pathname is relative then the symlink is created relative to\n"
"the directory referred to by the directory file descriptor dfd.\n"
);

static PyObject * fslib_symlinkat(PyObject *self, PyObject *args)
{
    char * srcpath = NULL;
    int dirfd;
    char * sinkpath = NULL;
    int sts;

    if (!PyArg_ParseTuple(args, "etiet:symlinkat",
                          Py_FileSystemDefaultEncoding, &srcpath,
                          &dirfd,
                          Py_FileSystemDefaultEncoding, &sinkpath)) {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    sts = symlinkat(srcpath, dirfd, sinkpath);
    Py_END_ALLOW_THREADS

    if (sts != 0) {
        PyErr_SetFromErrnoWithFilename(PyExc_OSError, sinkpath);
        PyMem_Free(srcpath);
        PyMem_Free(sinkpath);
        return NULL;
    }
    PyMem_Free(srcpath);
    PyMem_Free(sinkpath);
    Py_RETURN_NONE;
}


PyDoc_STRVAR(fslib_renameat__doc__,
"renameat(olddfd, oldpath, newfd, newpath)\n\n"
"Rename a file in a manner similar to os.rename\n"
"If either oldpath or newpath is relative then the file being renamed\n"
"is relative the directory referred to by the the directory file\n"
"descriptor preceding it.\n"
);

static PyObject * fslib_renameat(PyObject *self, PyObject *args)
{
    int olddirfd;
    char * oldpath = NULL;
    int newdirfd;
    char * newpath = NULL;
    int sts;

    if (!PyArg_ParseTuple(args, "ietiet:renameat",
                          &olddirfd,
                          Py_FileSystemDefaultEncoding, &oldpath,
                          &newdirfd,
                          Py_FileSystemDefaultEncoding, &newpath)) {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    sts = renameat(olddirfd, oldpath, newdirfd, newpath);
    Py_END_ALLOW_THREADS

    if (sts != 0) {
        PyErr_SetFromErrnoWithFilename(PyExc_OSError, newpath);
        PyMem_Free(oldpath);
        PyMem_Free(newpath);
        return NULL;
    }
    PyMem_Free(oldpath);
    PyMem_Free(newpath);
    Py_RETURN_NONE;
}


PyDoc_STRVAR(fslib_linkat__doc__,
"renameat(olddfd, oldpath, newfd, newpath)\n\n"
"Create a file link (aka hardlink), like os.link\n"
"If either oldpath or newpath is relative then the file being renamed\n"
"is relative the directory referred to by the the directory file\n"
"descriptor preceding it.\n"
);

static PyObject * fslib_linkat(PyObject *self, PyObject *args)
{
    int olddirfd;
    char * oldpath = NULL;
    int newdirfd;
    char * newpath = NULL;
    int flags = 0;
    int sts;

    if (!PyArg_ParseTuple(args, "ietiet:linkat",
                          &olddirfd,
                          Py_FileSystemDefaultEncoding, &oldpath,
                          &newdirfd,
                          Py_FileSystemDefaultEncoding, &newpath,
                          &flags)) {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    sts = linkat(olddirfd, oldpath, newdirfd, newpath, flags);
    Py_END_ALLOW_THREADS

    if (sts != 0) {
        PyErr_SetFromErrnoWithFilename(PyExc_OSError, newpath);
        PyMem_Free(oldpath);
        PyMem_Free(newpath);
        return NULL;
    }
    PyMem_Free(oldpath);
    PyMem_Free(newpath);
    Py_RETURN_NONE;
}


PyDoc_STRVAR(fslib_stat_obj__doc__,
MODULE_NAME ".stat_obj: wrapper for stat struct"
);


static PyStructSequence_Field fslib_stat_obj_fields[] = {
    {"st_mode", "protection bits"},
    {"st_ino", "inode"},
    {"st_dev", "device"},
    {"st_nlink", "number of hard links"},
    {"st_uid", "user ID of owner"},
    {"st_gid", "group ID of owner"},
    {"st_size", "total size, in bytes"},
    {"st_atime", "time of last access"},
    {"st_mtime", "time of last modification"},
    {"st_ctime", "time of last change"},
#ifdef HAVE_STRUCT_STAT_ST_BLKSIZE
    {"st_blksize", "block size"},
#endif
#ifdef HAVE_STRUCT_STAT_ST_BLOCKS
    {"st_blocks", "number of blocks"},
#endif
#ifdef HAVE_STRUCT_STAT_ST_RDEV
    {"st_rdev", "device type"},
#endif
    {0}
};


static PyStructSequence_Desc fslib_stat_obj_desc = {
    "fslib_stat_obj",
    fslib_stat_obj__doc__,
    fslib_stat_obj_fields,
    10
};


static PyTypeObject StatObjType;


#ifdef HAVE_LONG_LONG
#define Py_ST_DEV PyLong_FromLongLong
#define C_ST_DEV PY_LONG_LONG
#else
#define Py_ST_DEV PyInt_FromLong
#define C_ST_DEV long
#endif

#ifdef HAVE_LARGEFILE_SUPPORT
#define Py_ST_INT PyLong_FromLongLong
#define C_ST_INT PY_LONG_LONG
#else
#define Py_ST_INT PyInt_FromLong
#define C_ST_INT long
#endif


static PyObject *convert_stat_obj(struct stat *stp)
{
    int pos = 0;
    PyObject *res = PyStructSequence_New(&StatObjType);
    if (!res) return NULL;

    PyStructSequence_SET_ITEM(res, (pos++),
                              PyInt_FromLong((long)stp->st_mode));
    PyStructSequence_SET_ITEM(res, (pos++),
                              Py_ST_INT((C_ST_INT)stp->st_ino));
    PyStructSequence_SET_ITEM(res, (pos++),
                              Py_ST_DEV((C_ST_DEV)stp->st_dev));
    PyStructSequence_SET_ITEM(res, (pos++),
                              PyInt_FromLong((long)stp->st_nlink));
    PyStructSequence_SET_ITEM(res, (pos++),
                              PyInt_FromLong((long)stp->st_uid));
    PyStructSequence_SET_ITEM(res, (pos++),
                              PyInt_FromLong((long)stp->st_gid));
    PyStructSequence_SET_ITEM(res, (pos++),
                              Py_ST_INT((C_ST_INT)stp->st_size));

    PyStructSequence_SET_ITEM(res, (pos++),
                              PyFloat_FromDouble((double)stp->st_atime));
    PyStructSequence_SET_ITEM(res, (pos++),
                              PyFloat_FromDouble((double)stp->st_mtime));
    PyStructSequence_SET_ITEM(res, (pos++),
                              PyFloat_FromDouble((double)stp->st_ctime));

#ifdef HAVE_STRUCT_STAT_ST_BLKSIZE
    PyStructSequence_SET_ITEM(res, (pos++),
                              PyInt_FromLong((long)stp->st_blksize));
#endif
#ifdef HAVE_STRUCT_STAT_ST_BLOCKS
    PyStructSequence_SET_ITEM(res, (pos++),
                              PyInt_FromLong((long)stp->st_blocks));
#endif
#ifdef HAVE_STRUCT_STAT_ST_RDEV
    PyStructSequence_SET_ITEM(res, (pos++),
                              PyInt_FromLong((long)stp->st_rdev));
#endif
    return res;
}


PyDoc_STRVAR(fslib_fstatat__doc__,
"fstatat(dirfd, pathname [, flags]) -> stat data\n\n"
"Retrieve the stat data for a file, like os.stat.\n"
"If pathname is relative then the file is accessed relative to\n"
"the directory referred to by the directory file descriptor dfd.\n"
"Returns a dict containing the stat fields for this platform.\n"
);

static PyObject * fslib_fstatat(PyObject *self, PyObject *args)
{
    int dirfd;
    char * path = NULL;
    int flags = 0;
    int sts;
    struct stat statbuf;

    if (!PyArg_ParseTuple(args, "iet|i:fstatat",
                          &dirfd,
                          Py_FileSystemDefaultEncoding, &path,
                          &flags)) {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    sts = fstatat(dirfd, path, &statbuf, flags);
    Py_END_ALLOW_THREADS

    if (sts != 0) {
        return bail_like_posix(path);
    }
    PyMem_Free(path);
    return convert_stat_obj(&statbuf);
}

/* define my own time pair type
 * this makes it easier to convert to other time structs
 */
struct timepair {
    time_t seconds;
    long fraction;
    double scale;
};


static int store_time_arg(struct timepair times[], int pos,
                          PyObject *ptime)
{
    long wholesec;
    double fracsec;
    if (PyFloat_Check(ptime)) {
        wholesec = PyInt_AsLong(ptime);
        fracsec = PyFloat_AsDouble(ptime);
        times[pos].seconds = wholesec;
        times[pos].fraction = (long)((fracsec - wholesec) * times[0].scale);
        if (times[pos].fraction < 0) {
            /* not allowed to be negative */
            times[pos].fraction = 0;
        }
        return 0;
    }
    if (PyInt_Check(ptime)) {
        times[pos].seconds = PyInt_AsLong(ptime);
        times[pos].fraction = 0;
        return 0;
    }
    if (PyTuple_Check(ptime) && PyTuple_Size(ptime) == 2
        && PyInt_Check(PyTuple_GET_ITEM(ptime, 0))
        && PyInt_Check(PyTuple_GET_ITEM(ptime, 1))) {
        times[pos].seconds = (time_t)PyInt_AsLong(PyTuple_GET_ITEM(ptime, 0));
        times[pos].fraction = PyInt_AsLong(PyTuple_GET_ITEM(ptime, 1));
        return 0;
    }
    PyErr_SetString(PyExc_TypeError,
                    (pos==0)?
                        ("atime must be a tuple (sec, nsec) or number"):
                        ("mtime must be a tuple (sec, nsec) or number"));
    return -1;
}

static int pyarg_to_timespec(struct timepair times[], PyObject *timearg)
{
    PyObject * atime;
    PyObject * mtime;

    if (timearg == Py_None) {
        return 0;
    }
    if (PyTuple_Check(timearg) && PyTuple_Size(timearg) == 2) {
        atime = PyTuple_GET_ITEM(timearg, 0);
        mtime = PyTuple_GET_ITEM(timearg, 1);
        if (store_time_arg(times, 0, atime) == -1) {
            return -1;
        }
        if (store_time_arg(times, 1, mtime) == -1) {
            return -1;
        }
        return 1;
    }
    PyErr_SetString(PyExc_TypeError, "arg 2 must be a tuple (atime, mtime)");
    return -1;
}

#if HAVE_UTIMENSAT

PyDoc_STRVAR(fslib_utimensat__doc__,
"utimensat(dirfd, pathname, (atime, mtime))\n\n"
"Set the access and modified times on a file, like os.utime.\n"
"The time tuple may be given as a single None value to set both\n"
"atime and mtime to the current time. Otherwise, atime and mtime\n"
"must both be either an integer a float or a two-tuple containing\n"
"the time value in seconds followed by a value in nanoseconds.\n"
"If pathname is relative then the file is accessed relative to\n"
"the directory referred to by the directory file descriptor dfd.\n"
);

static PyObject * fslib_utimensat(PyObject *self, PyObject *args)
{
    int dirfd;
    char * path = NULL;
    PyObject *timearg;
    int flags = 0;
    int sts;
    struct timepair timetemp[2];
    struct timespec times[2];


    if (!PyArg_ParseTuple(args, "ietO|i:utimensat",
                          &dirfd,
                          Py_FileSystemDefaultEncoding, &path,
                          &timearg,
                          &flags)) {
        return NULL;
    }

    timetemp[0].scale = 1e9;
    timetemp[1].scale = 1e9;
    sts = pyarg_to_timespec(timetemp, timearg);
    if (sts == -1) {
        PyMem_Free(path);
        return NULL;
    }
    times[0].tv_sec = timetemp[0].seconds;
    times[0].tv_nsec = timetemp[0].fraction;
    times[1].tv_sec = timetemp[1].seconds;
    times[1].tv_nsec = timetemp[1].fraction;

    Py_BEGIN_ALLOW_THREADS
    if (sts == 0) {
        sts = utimensat(dirfd, path, NULL, flags);
    } else {
        sts = utimensat(dirfd, path, times, flags);
    }
    Py_END_ALLOW_THREADS

    if (sts != 0) {
        return bail_like_posix(path);
    }
    PyMem_Free(path);
    Py_RETURN_NONE;
}

#endif /* HAVE_UTIMENSAT */


#if defined(HAVE_FUTIMESAT)

PyDoc_STRVAR(fslib_futimesat__doc__,
"futimesat(dirfd, pathname, (atime, mtime))\n\n"
"Set the access and modified times on a file, like os.utime.\n"
"The time tuple may be given as a single None value to set both\n"
"atime and mtime to the current time. Otherwise, atime and mtime\n"
"must both be either an integer a float or a two-tuple containing\n"
"the time value in seconds followed by a value in nanoseconds.\n"
"If pathname is relative then the file is accessed relative to\n"
"the directory referred to by the directory file descriptor dfd.\n"
);

static PyObject * fslib_futimesat(PyObject *self, PyObject *args)
{
    int dirfd;
    char * path = NULL;
    PyObject *timearg;
    int sts;
    struct timepair timetemp[2];
    struct timeval times[2];


    if (!PyArg_ParseTuple(args, "ietO|i:futimesat",
                          &dirfd,
                          Py_FileSystemDefaultEncoding, &path,
                          &timearg)) {
        return NULL;
    }

    timetemp[0].scale = 1e6;
    timetemp[1].scale = 1e6;
    sts = pyarg_to_timespec(timetemp, timearg);
    if (sts == -1) {
        PyMem_Free(path);
        return NULL;
    }
    times[0].tv_sec = timetemp[0].seconds;
    times[0].tv_usec = timetemp[0].fraction;
    times[1].tv_sec = timetemp[1].seconds;
    times[1].tv_usec = timetemp[1].fraction;

    Py_BEGIN_ALLOW_THREADS
    if (sts == 0) {
        sts = futimesat(dirfd, path, NULL);
    } else {
        sts = futimesat(dirfd, path, times);
    }
    Py_END_ALLOW_THREADS

    if (sts != 0) {
        return bail_like_posix(path);
    }
    PyMem_Free(path);
    Py_RETURN_NONE;
}

#endif /* defined(HAVE_FUTIMESAT) */

/*
 * _append_dir_entries is used to append ``max`` directory entries to
 * the list ``pylist`` by reading them out of ``dirh``. The number
 * of items read will be placed into ``count``. ``flags`` are used to
 * control the behavior of the listing (currently only including DTYPE).
 *
 * The behavior of this function should be pretty similar to the behavior
 * of posixmodule.c in python stdlib. The main differences are the adding
 * to an existing list, and the control flags.
 */
int _append_dir_entries(DIR *dirh, PyObject *pylist, unsigned int max,
                        unsigned int flags, unsigned int *count)
{
    int failure = 0;
    unsigned int curr = 0;
    struct dirent *dent;
    size_t slen;
    PyObject *fn;

    for (;;) {
        if (max && curr>=max) {
            break; /* over max */
        }
        errno = 0;
        Py_BEGIN_ALLOW_THREADS
        dent = readdir(dirh);
        Py_END_ALLOW_THREADS

        if (dent == NULL && errno == 0) {
            break; /* end of the dir stream */
        }
        if (dent == NULL) {
            failure = errno;
            break; /* error condition */
        }

        slen = strlen(dent->d_name);
        if ((slen == 1 && dent->d_name[0] == '.') ||
            (slen == 2 && dent->d_name[0] == '.' && dent->d_name[1] == '.')) {
            continue;
        }
        fn = PyString_FromStringAndSize(dent->d_name, slen);
        if (fn == NULL ) {
            failure = -1;
            break; /* error condition */
        }
        if (flags & INCL_DTYPE) {
            fn = Py_BuildValue("NB", fn, dent->d_type);
            if (fn == NULL ) {
                failure = -1;
                break; /* error condition */
            }
        }
        if (PyList_Append(pylist, fn) != 0) {
            Py_XDECREF(fn);
            failure = -1;
            break; /* error condition */
        } else {
            Py_XDECREF(fn);
        }
    }

    (*count) = curr;
    return failure;
}


PyDoc_STRVAR(fslib_fdlistdir__doc__,
"fdlistdir(fd, flags=0) -> list of strings\n\n"
"Return a list of the names of the entries in the directory.");

static PyObject * fslib_fdlistdir(PyObject *self, PyObject *args)
{
    int dirfd;
    DIR *dirh;
    PyObject *reslist;
    int res;
    unsigned int count;
    unsigned int flags = 0;

    if (!PyArg_ParseTuple(args, "i|i:fdlistdir", &dirfd, &flags)) {
        return NULL;
    }

    reslist = PyList_New(0);
    if (reslist == NULL) return NULL;

    dirfd = dup(dirfd);
    if (dirfd < 0) {
        Py_XDECREF(reslist);
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }
    dirh = fdopendir(dirfd);
    if (dirh == NULL) {
        Py_XDECREF(reslist);
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }
    rewinddir(dirh);

    res = _append_dir_entries(dirh, reslist, 0, flags, &count);
    if (res > 0) {
        Py_XDECREF(reslist);
        closedir(dirh);
        errno = res;
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }
    if (res != 0) {
        Py_XDECREF(reslist);
        closedir(dirh);
        PyErr_SetString(PyExc_MemoryError, "could not update dir list");
        return NULL;
    }

    closedir(dirh);
    return reslist;
}


PyDoc_STRVAR(fslib_listdir__doc__,
"listdir(path, flags=0) -> list of strings\n\n"
"Return a list of the names of the entries in the directory.");

static PyObject * fslib_listdir(PyObject *self, PyObject *args)
{
    char *path = NULL;
    DIR *dirh;
    PyObject *reslist = NULL;
    int res;
    unsigned int count;
    unsigned int flags = 0;

    if (!PyArg_ParseTuple(args, "et|i:fdlistdir",
                          Py_FileSystemDefaultEncoding, &path,
                          &flags)) {
        return NULL;
    }

    reslist = PyList_New(0);
    if (reslist == NULL)
      goto fail;

    dirh = opendir(path);
    if (dirh == NULL) {
        Py_XDECREF(reslist);
        bail_like_posix(path);
        return NULL;
    }
    rewinddir(dirh);

    res = _append_dir_entries(dirh, reslist, 0, flags, &count);
    if (res > 0) {
        Py_XDECREF(reslist);
        closedir(dirh);
        errno = res;
        bail_like_posix(path);
        return NULL;
    }
    if (res != 0) {
        Py_XDECREF(reslist);
        closedir(dirh);
        PyErr_SetString(PyExc_MemoryError, "could not update dir list");
        reslist = NULL;
        goto fail;
    }

    closedir(dirh);

fail:
    PyMem_Free(path);
    return reslist;
}

/*
 * Implement the iterator object returned by fditerdir
 */

typedef struct {
    PyObject_HEAD
    /* object specific fields */
    DIR *dirh;
    PyObject *entries;
    unsigned int groupsize;
    unsigned int flags;
} fslib_diriter;


static void fslib_diriter_dealloc(fslib_diriter *self)
{
    Py_XDECREF(self->entries);
    if (self->dirh != NULL) {
        closedir(self->dirh);
        self->dirh = NULL;
    }
    self->ob_type->tp_free((PyObject*)self);
}


static PyObject * fslib_diriter_new(PyTypeObject *type,
                                   PyObject *args,
                                   PyObject *kwds)
{
    fslib_diriter *self;

    self = (fslib_diriter *)type->tp_alloc(type, 0);
    self->entries = PyList_New(0);
    if (self->entries == NULL) {
        PyErr_SetString(PyExc_MemoryError, "failed allocation");
        return NULL;
    }
    self->dirh = NULL;
    return (PyObject *)self;
}


static PyTypeObject fslib_diriter_type = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "fslib.DirIter",           /*tp_name*/
    sizeof(fslib_diriter),     /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)fslib_diriter_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "directory iter",          /* tp_doc */

};


static PyObject *fslib_diriter_iter(fslib_diriter *self)
{
    Py_XINCREF((PyObject *)self);
    return (PyObject*)self;
}


static PyObject *fslib_diriter_next(fslib_diriter *self)
{
    int res;
    unsigned int count = 0;
    PyObject *result = NULL;

    if (self->dirh == NULL) {
        PyErr_SetString(PyExc_StopIteration, "");
        return NULL;
    }

    if (PyList_Size(self->entries) < 1) {
        res = _append_dir_entries(self->dirh, self->entries,
                                  self->groupsize, self->flags, &count);
        if (res > 0) {
            errno = res;
            PyErr_SetFromErrno(PyExc_OSError);
            return NULL;
        }
        if (res != 0) {
            PyErr_SetString(PyExc_MemoryError, "could not update dir list");
            return NULL;
        }
        if (PyList_Size(self->entries) == 0) {
            if (closedir(self->dirh) != 0) {
                PyErr_SetFromErrno(PyExc_OSError);
            } else {
                PyErr_SetString(PyExc_StopIteration, "");
            }
            self->dirh = NULL;
            return NULL;
        }
    }

    result = PySequence_GetItem(self->entries, 0);
    if (result == NULL || PySequence_DelItem(self->entries, 0) == -1) {
        return NULL;
    }

    return result;
}


static PyObject *fslib_diriter_enter(fslib_diriter *self, PyObject *args)
{
    /* guess what happens if this incref isn't here - oh yeah! */
    Py_XINCREF((PyObject *)self);
    return (PyObject *)self;
}


static PyObject *fslib_diriter_exit(fslib_diriter *self, PyObject *args)
{
    if (self->dirh != NULL) {
        closedir(self->dirh);
        self->dirh = NULL;
    }
    Py_RETURN_NONE;
}


static PyObject *fslib_diriter_close(fslib_diriter *self, PyObject *args)
{
    if (self->dirh != NULL) {
        closedir(self->dirh);
        self->dirh = NULL;
    }
    Py_RETURN_NONE;
}


static PyMethodDef fslib_diriter_methods[] = {
    {"__iter__", (PyCFunction)fslib_diriter_iter, METH_NOARGS,
            "return the iterator"},
    {"next", (PyCFunction)fslib_diriter_next, METH_NOARGS,
            "return next item"},
    {"close", (PyCFunction)fslib_diriter_close, METH_NOARGS,
            "close directory pointer"},
    {"__enter__", (PyCFunction)fslib_diriter_enter, METH_NOARGS,
            "enter a context manager"},
    {"__exit__", (PyCFunction)fslib_diriter_exit, METH_VARARGS,
            "exit the context manager"},

    {NULL}
};


PyDoc_STRVAR(fslib_fditerdir__doc__,
"fditerdir(dirfd) -> iterator\n\n"
"Return an iterator that yields the names of the entries in the directory.");


PyObject *fslib_fditerdir(PyObject *self, PyObject *args)
{
    int dirfd;
    int groupsize = 32;
    DIR *temp;
    int flags = 0;
    fslib_diriter *obj;

    if (!PyArg_ParseTuple(args, "i|ii:fditerdir", &dirfd, &groupsize, &flags)) {
        return NULL;
    }

    dirfd = dup(dirfd);
    if (dirfd < 0) {
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }
    Py_BEGIN_ALLOW_THREADS
    temp = fdopendir(dirfd);
    Py_END_ALLOW_THREADS
    if (temp == NULL) {
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }
    rewinddir(temp);

    obj = (fslib_diriter*)fslib_diriter_new(&fslib_diriter_type, NULL, NULL);
    if (obj == NULL) {
        closedir(temp);
        return NULL;
    } else {
        obj->dirh = temp;
    }

    obj->flags = flags;
    obj->groupsize = groupsize;
    return (PyObject*)obj;
}


static PyMethodDef Methods[] = {
    {"openat", fslib_openat, METH_VARARGS, fslib_openat__doc__},
    {"unlinkat", fslib_unlinkat, METH_VARARGS, fslib_unlinkat__doc__},
    {"mkfifoat", fslib_mkfifoat, METH_VARARGS, fslib_mkfifoat__doc__},
    {"mkdirat", fslib_mkdirat, METH_VARARGS, fslib_mkdirat__doc__},
    {"mknodat", fslib_mknodat, METH_VARARGS, fslib_mknodat__doc__},
    {"fchownat", fslib_fchownat, METH_VARARGS, fslib_fchownat__doc__},
    {"fchmodat", fslib_fchmodat, METH_VARARGS, fslib_fchmodat__doc__},
    {"faccessat", fslib_faccessat, METH_VARARGS, fslib_faccessat__doc__},
    {"readlinkat", fslib_readlinkat, METH_VARARGS, fslib_readlinkat__doc__},
    {"symlinkat", fslib_symlinkat, METH_VARARGS, fslib_symlinkat__doc__},
    {"renameat", fslib_renameat, METH_VARARGS, fslib_renameat__doc__},
    {"linkat", fslib_linkat, METH_VARARGS, fslib_linkat__doc__},
    {"fstatat", fslib_fstatat, METH_VARARGS, fslib_fstatat__doc__},
#if HAVE_UTIMENSAT
    {"utimensat", fslib_utimensat, METH_VARARGS, fslib_utimensat__doc__},
#endif
#if defined(HAVE_FUTIMESAT)
    {"futimesat", fslib_futimesat, METH_VARARGS, fslib_futimesat__doc__},
#endif

    {"fdlistdir", fslib_fdlistdir, METH_VARARGS, fslib_fdlistdir__doc__},
    {"listdir", fslib_listdir, METH_VARARGS, fslib_listdir__doc__},
    {"fditerdir", fslib_fditerdir, METH_VARARGS, fslib_fditerdir__doc__},

    {NULL, NULL, 0, NULL}
};


PyMODINIT_FUNC initfslib(void)
{
    PyObject *mod;
    mod = Py_InitModule(MODULE_NAME, Methods);
    int res;

    /* flag constants */
    res = PyModule_AddIntConstant(mod, "AT_FDCWD", AT_FDCWD);
    if (res) return;
    res = PyModule_AddIntConstant(mod, "AT_REMOVEDIR", AT_REMOVEDIR);
    if (res) return;
    res = PyModule_AddIntConstant(mod, "AT_EACCESS", AT_EACCESS);
    if (res) return;
    res = PyModule_AddIntConstant(mod,
                                  "AT_SYMLINK_NOFOLLOW",
                                  AT_SYMLINK_NOFOLLOW);
    if (res) return;

    /* misc flags */
    res = PyModule_AddIntConstant(mod, "O_CLOEXEC", O_CLOEXEC);
    if (res) return;
    /* directory entry flags */
    res = PyModule_AddIntConstant(mod, "DT_UNKNOWN", DT_UNKNOWN);
    if (res) return;
    res = PyModule_AddIntConstant(mod, "DT_BLK", DT_BLK);
    if (res) return;
    res = PyModule_AddIntConstant(mod, "DT_CHR", DT_CHR);
    if (res) return;
    res = PyModule_AddIntConstant(mod, "DT_DIR", DT_DIR);
    if (res) return;
    res = PyModule_AddIntConstant(mod, "DT_FIFO", DT_FIFO);
    if (res) return;
    res = PyModule_AddIntConstant(mod, "DT_LNK", DT_LNK);
    if (res) return;
    res = PyModule_AddIntConstant(mod, "DT_REG", DT_REG);
    if (res) return;
    res = PyModule_AddIntConstant(mod, "DT_SOCK", DT_SOCK);
    if (res) return;


    /* configuration constants */
    res = PyModule_AddIntConstant(mod, "HAVE_UTIMENSAT", HAVE_UTIMENSAT);
    if (res) return;
    res = PyModule_AddIntConstant(mod, "HAVE_FUTIMESAT", HAVE_FUTIMESAT);
    if (res) return;
    res = PyModule_AddIntConstant(mod, "FSLIB_INCL_DTYPE", INCL_DTYPE);
    if (res) return;

    fslib_diriter_type.tp_new = fslib_diriter_new;
    fslib_diriter_type.tp_methods = fslib_diriter_methods;
    if (PyType_Ready(&fslib_diriter_type) < 0) {
        return;
    }
    Py_INCREF(&fslib_diriter_type);
    PyModule_AddObject(mod, "DirIter",
                      (PyObject *)&fslib_diriter_type);

    PyStructSequence_InitType(&StatObjType, &fslib_stat_obj_desc);
    Py_INCREF((PyObject*) &StatObjType);
    PyModule_AddObject(mod, "stat_obj", (PyObject*) &StatObjType);
}
