#!/usr/bin/env python
# 
# Copyright (c) 2011, 2012 Nasuni Corporation  http://www.nasuni.com/
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
"""fswlib - Ctypes wrappers for posix.1-2008 and other system calls

Exposes posix functions like openat, unlinkat and such to
python. These newer posix functions are not exposed by
the python standard library in python 2.x.
"""

import ctypes
import ctypes.util
import sys
import os
import collections

from ctypes import c_int, c_char_p

__all__ = [
    'HAVE_FUTIMESAT',
    'HAVE_UTIMENSAT',
    'AT_FDCWD',
    'AT_SYMLINK_NOFOLLOW',
    'AT_EACCESS',
    'AT_REMOVEDIR',
    'faccessat',
    'fchmodat',
    'fchownat',
    'fditerdir',
    'fdlistdir',
    'fstatat',
    'futimesat',
    'linkat',
    'mkdirat',
    'mkfifoat',
    'mknodat',
    'openat',
    'readlinkat',
    'renameat',
    'symlinkat',
    'unlinkat',
    'utimensat',
    ]


try:
    _libcpath = ctypes.util.find_library('c')
except Exception:
    _libcpath = None
if not _libcpath:
    raise ImportError('can not find libc')


_libc = ctypes.CDLL(_libcpath, use_errno=True)


HAVE_UTIMENSAT = bool(getattr(_libc, 'utimensat', None))
HAVE_FUTIMESAT = bool(getattr(_libc, 'futimesat', None))
try:
    MAXPATH = os.pathconf('/', 'PC_PATH_MAX')
except Exception:
    MAXPATH = 1024


_libc.rewinddir.argtypes = (ctypes.c_void_p,)


def _exc_from_errno(ecls, msg=None, path=None):
    eno = ctypes.get_errno()
    if not msg:
        msg = os.strerror(eno)
    if path:
        return ecls(eno, msg, path)
    else:
        return ecls(eno, msg)


def openat(fd, pathname, flags=0, mode=0600):
    try:
        _openat = _libc.openat64
    except AttributeError:
        # fall back to openat if openat64 does not exist
        _openat = _libc.openat
    _openat.argtypes = (c_int, c_char_p, c_int, c_int)
    _openat.restype = c_int
    res = _openat(fd, pathname, int(flags), int(mode))
    if res == -1:
        raise _exc_from_errno(IOError, path=pathname)
    return res


def renameat(oldfd, oldpath, newfd, newpath):
    """renameat
    """
    _renameat = _libc.renameat
    _renameat.argtypes = (c_int, c_char_p, c_int, c_char_p)
    _renameat.restype = c_int
    res = _renameat(oldfd, oldpath, newfd, newpath)
    if res == -1:
        raise _exc_from_errno(OSError, path=newpath)
    return res


def mkdirat(fd, path, mode=0777):
    """mkdirat
    """
    _mkdirat = _libc.mkdirat
    _mkdirat.argtypes = (c_int, c_char_p, c_int)
    _mkdirat.restype = c_int
    res = _mkdirat(fd, path, int(mode))
    if res == -1:
        raise _exc_from_errno(OSError, path=path)
    return res


def mkfifoat(fd, path, mode=0666):
    _mkfifoat = _libc.mkfifoat
    _mkfifoat.argtypes = (c_int, c_char_p, c_int)
    _mkfifoat.restype = c_int
    res = _mkfifoat(fd, path, int(mode))
    if res == -1:
        raise _exc_from_errno(OSError, path=path)
    return res


def mknodat(fd, path, mode=0600, device=0):
    _mknodat = _libc.mknodat
    _mknodat.argtypes = (c_int, c_char_p, c_int, c_int)
    _mknodat.restype = c_int
    res = _mknodat(fd, path, int(mode), int(device))
    if res == -1:
        raise _exc_from_errno(OSError, path=path)
    return res


def linkat(oldfd, oldpath, newfd, newpath, flags=0):
    _linkat = _libc.linkat
    _linkat.argtypes = (c_int, c_char_p, c_int, c_char_p, c_int)
    _linkat.restype = c_int
    res = _linkat(oldfd, oldpath, newfd, newpath, int(flags))
    if res == -1:
        raise _exc_from_errno(OSError, path=newpath)
    return res


def symlinkat(oldname, fd, name):
    """create a symlink to `oldname` at name
    """
    _symlinkat = _libc.symlinkat
    _symlinkat.argtypes = (c_char_p, c_int, c_char_p)
    _symlinkat.restype = c_int
    res = _symlinkat(oldname, fd, name)
    if res == -1:
        raise _exc_from_errno(OSError, path=name)
    return res


def unlinkat(fd, path, flags=0):
    """unlinkat
    """
    _unlinkat = _libc.unlinkat
    _unlinkat.argtypes = (c_int, c_char_p, c_int)
    _unlinkat.restype = c_int
    res = _unlinkat(fd, path, int(flags))
    if res == -1:
        raise _exc_from_errno(OSError, path=path)
    return res


def readlinkat(fd, path):
    """readlinkat
    """
    _readlinkat = _libc.readlinkat
    _readlinkat.argtypes = (c_int, c_char_p, c_char_p, ctypes.c_size_t)
    _readlinkat.restype = c_int
    obuf = ctypes.create_string_buffer(MAXPATH)
    res = _readlinkat(fd, path, obuf, ctypes.sizeof(obuf))
    if res == -1:
        raise _exc_from_errno(OSError, path=path)
    return obuf.value


def fchownat(fd, path, uid, gid, flags=0):
    _fchownat = _libc.fchownat
    _fchownat.argtypes = (c_int, c_char_p, c_int, c_int, c_int)
    _fchownat.restype = c_int
    res = _fchownat(fd, path, int(uid), int(gid), int(flags))
    if res == -1:
        raise _exc_from_errno(OSError, path=path)
    return res


def fchmodat(fd, path, mode, flags=0):
    _fchmodat = _libc.fchmodat
    _fchmodat.argtypes = (c_int, c_char_p, c_int, c_int)
    _fchmodat.restype = c_int
    res = _fchmodat(fd, path, int(mode), int(flags))
    if res == -1:
        raise _exc_from_errno(OSError, path=path)
    return res


class _stat(ctypes.Structure):
    """
    Currently Linux Only -- not checked for portability

           struct stat {
               dev_t     st_dev;     /* ID of device containing file */
               ino_t     st_ino;     /* inode number */
               mode_t    st_mode;    /* protection */
               nlink_t   st_nlink;   /* number of hard links */
               uid_t     st_uid;     /* user ID of owner */
               gid_t     st_gid;     /* group ID of owner */
               dev_t     st_rdev;    /* device ID (if special file) */
               off_t     st_size;    /* total size, in bytes */
               blksize_t st_blksize; /* blocksize for file system I/O */
               blkcnt_t  st_blocks;  /* number of 512B blocks allocated */
               time_t    st_atime;   /* time of last access */
               time_t    st_mtime;   /* time of last modification */
               time_t    st_ctime;   /* time of last status change */
           };
    """
    _fields_ = [
        ('st_dev', ctypes.c_ulong),
        ('st_ino', ctypes.c_ulong),
        ('st_mode', ctypes.c_uint),
        ('st_nlink', ctypes.c_ulong),
        ('st_uid', ctypes.c_uint),
        ('st_gid', ctypes.c_uint),
        ('st_rdev', ctypes.c_ulong),
        ('st_size', ctypes.c_ulong),
        ('st_blksize', ctypes.c_ulong),
        ('st_blocks', ctypes.c_ulong),
        ('st_atime', ctypes.c_long),
        ('st_mtime', ctypes.c_long),
        ('st_ctime', ctypes.c_long),
        ]

_stat_p = ctypes.POINTER(_stat)

statresult = collections.namedtuple('statresult',
        'st_mode st_ino st_dev st_nlink st_uid st_gid st_size'
        ' st_atime st_mtime st_ctime st_blksize st_blocks st_rdev')


def fstatat(fd, path, flags=0):
    raise NotImplementedError()
    """
    _fstatat = _libc.__fxstatat64
    _fstatat.argtypes = (c_int, c_int, c_char_p, ctypes.c_void_p, c_int)
    _fstatat.restype = c_int
    s = _stat()
    res = _fstatat(1, fd, path, ctypes.byref(x), int(flags))
    if res == -1:
        raise _exc_from_errno(OSError, path=path)
    return None
    return ctypes.cast(x, _stat)
    return _stat_tuple(s)
    """


def _stat_tuple(stat_struct):
    return statresult(**dict((k, getattr(stat_struct, k))
                              for k in statresult._fields))


def faccessat(fd, path, mode, flags=0):
    _faccessat = _libc.faccessat
    _faccessat.argtypes = (c_int, c_char_p, c_int, c_int)
    _faccessat.restype = c_int
    res = _faccessat(fd, path, mode, flags)
    return (res == 0)


def futimesat(fd, path, times):
    #futimesat(dirfd, pathname, (atime, mtime))
    raise NotImplementedError()


def utimensat(fd, path, times):
    #utimensat(dirfd, pathname, (atime, mtime))
    raise NotImplementedError()


class dirent(ctypes.Structure):
    _fields_ = [
        ('d_ino', ctypes.c_ulong),
        ('d_off', ctypes.c_ulong),
        ('d_reclen', ctypes.c_ushort),
        ('d_type', ctypes.c_char),
        ('d_name', ctypes.c_char * 256),
        ]


class dirent_fbsd(ctypes.Structure):
    _fields_ = [
        ('d_fileno', ctypes.c_uint32),
        ('d_reclen', ctypes.c_uint16),
        ('d_type', ctypes.c_uint8),
        ('d_namelen', ctypes.c_uint8),
        ('d_name', ctypes.c_char * 256),
        ]


def _fdopendir(fd):
    _fdod = _libc.fdopendir
    _fdod.argtypes = (c_int,)
    _fdod.restype = ctypes.c_void_p
    res = _fdod(fd)
    if res is None:
        raise _exc_from_errno(OSError)
    return res


def _closedir(dirh):
    _cld = _libc.closedir
    _cld.argtypes = (ctypes.c_void_p,)
    _cld.restype = c_int
    res = _cld(dirh)
    if res == -1:
        raise _exc_from_errno(OSError)
    return res


def _readdir(dirh):
    _readd = _libc.readdir
    _readd.argtypes = (ctypes.c_void_p,)
    _readd.restype = dirent_p
    ent = _readd(dirh)
    if ent:
        return ent.contents.d_name
    else:
        return ''


def _filldirs(dirh, items, maxitems):
    curr = 0
    while True:
        if maxitems and curr >= maxitems:
            break
        ent = _readdir(dirh)
        if ent == '.' or ent == '..':
            continue
        elif ent:
            items.append(ent)
        else:
            break
    return curr


def fdlistdir(fd):
    entries = []
    dirh = _fdopendir(os.dup(fd))
    try:
        _libc.rewinddir(dirh)
        _filldirs(dirh, entries, 0)
    finally:
        _closedir(dirh)
    return entries


def fditerdir(fd, groupsize=32):
    return _diriter(fd, groupsize)


class _diriter(object):
    __slots__ = ('fd', '_dirh', 'groupsize', '_buf')

    def __init__(self, fd, groupsize):
        self.fd = fd
        self.groupsize = groupsize
        self._dirh = _fdopendir(os.dup(fd))
        self._buf = []
        _libc.rewinddir(self._dirh)

    def close(self, _close=_closedir):
        if self._dirh:
            _close(self._dirh)
            self._dirh = None

    def __iter__(self):
        return self

    def next(self):
        if not self._dirh:
            raise StopIteration()
        if not self._buf:
            _filldirs(self._dirh, self._buf, self.groupsize)
            if not self._buf:
                self.close()
                raise StopIteration()
        return self._buf.pop(0)

    def __enter__(self):
        return self

    def __exit__(self, etype, exc, tb):
        self.close()

    def __del__(self):
        self.close()


# constants that are same cross platform
AT_FDCWD = -100


# some constants change from platform to platform
if sys.platform.startswith('freebsd'):
    dirent_p = ctypes.POINTER(dirent_fbsd)
    AT_REMOVEDIR = 0x800
    AT_EACCESS = 0x100
    AT_SYMLINK_NOFOLLOW = 0x200
    O_CLOEXEC = 0x00100000
else:
    dirent_p = ctypes.POINTER(dirent)
    AT_REMOVEDIR = 0x200
    AT_EACCESS = 0x200
    AT_SYMLINK_NOFOLLOW = 0x100
    O_CLOEXEC = 0x80000
