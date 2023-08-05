

fsnix.fslib - Low Level Wrappers
========================================

.. module:: fsnix.fslib
    :synopsis: System level (C-library) API wrappers


This module exposes the lowest level functions and system calls.
It it written in C and requires CPython 2.x compatible API to
compile. If something here is under-documented you should be able
to refer to the manpages on your system for details. Like the :mod:`os`
module error codes are raised as exceptions with errno's assigned.

Anywhere we can mimic the spirit of :mod:`os` we do, while at the
same time trying to minimize deviations from the low level C-API.


Module API
-------------

.. function:: faccessat(dirfd, pathname, mode)

    Return a boolean indicating that the current process has access
    to pathname relative to dirfd.
    Behaves in a manner similar to :func:`os.access`.

    If pathname is relative then the file is created relative to
    the directory referred to by the directory file descriptor *dirfd*.

    .. note::
       Currently, there is no mechanism to get the errno.

    .. warning::
       Using this function can lead to `time-of-check
       to time-of-use errors`_.


.. function:: fchmodat(dirfd, pathname, mode[, flags])

    Change the mode of the file given by *dirfd* and *pathname* 
    to the numeric *mode*.
    Behaves in a manner similar to :func:`os.fchmod`.

    If pathname is relative then the file is modified relative to
    the directory referred to by the directory file descriptor *dirfd*.
    Specifying the :const:`AT_SYMLINK_NOFOLLOW` flag will cause the function
    to operate on symlinks rather than the file it points to.


.. function:: fchownat(dirfd, pathname, uid, gid[, flags])

    Change the user and group ownership of a file, like :func:`os.chown`.
    The uid and gid parameters must be integers.

    If pathname is relative then the file is modified relative to
    the directory referred to by the directory file descriptor *dirfd*.
    Specifying the :const:`AT_SYMLINK_NOFOLLOW` flag will cause the function
    to operate on symlinks rather than the file it points to.


.. function:: fditerdir(dirfd[, flags])

    Return an iterator that yields the names of the entries in the 
    open directory located by *dirfd*.

    See the documentation of :func:`listdir` for details on the
    *flags* argument.
    
    .. note::
       This function will "consume" the file descriptor passed to it.
       If you need to re-use the descriptor later, create a duplicate
       via :func:`os.dup` first.


.. function:: fdlistdir(dirfd[, flags])

    Return a list of the names of the entries in the directory
    located by *dirfd*.

    See the documentation of :func:`listdir` for details on the
    *flags* argument.

    .. note::
       This function will "consume" the file descriptor passed to it.
       If you need to re-use the descriptor later, create a duplicate
       via :func:`os.dup` first.


.. function:: fstatat(dirfd, pathname[, flags])

    Return a stat structure for the file system entry indicated
    by *dirfd* and *pathname*.
    Behaves in a manner similar to :func:`os.stat`.

    If pathname is relative then the file is accessed relative to
    the directory referred to by the directory file descriptor *dirfd*.
    Specifying the :const:`AT_SYMLINK_NOFOLLOW` flag will cause the function
    to operate on symlinks rather than the file it points to.


.. function:: futimesat(dirfd, pathname, (atime, mtime)

    Set the access and modified times on a file.
    Behaves in a manner similar to :func:`os.utime`.

    The time tuple may be given as a single None value to set both
    atime and mtime to the current time. Otherwise, atime and mtime
    must both be either an integer, a float, or a two-tuple containing
    the time value in seconds followed by a value in microseconds.

    If pathname is relative then the file is modified relative to
    the directory referred to by the directory file descriptor *dirfd*.


.. function:: linkat(oldfd, oldpath, newfd, newpath)

    Create a hard link from the "old location" to the "new location".
    Behaves in a manner similar to :func:`os.link`.

    If either oldpath or newpath is relative then the file being linked
    is relative the directory referred to by the the directory file
    descriptor preceding it.
   

.. function:: listdir(path[, flags])

    Return a list of the names of the entries in the directory
    given by *path*. 
    Behaves in a manner similar to :func:`os.listdir` if no flags
    are specified.

    Passing the flag :const:`FSLIB_INCL_DTYPE` will return a list
    of tuples of the type (name, d_type) where d_type is an integer
    corresponding to the entries file system type, or zero if no
    type was fetched. See the `d_type constants`_ list for what
    values may appear here. 
    
    .. note:: 
        Not all file systems support d_type,
        so any code written to check the d_type should fall back to
        stat calls if the d_type is unknown.
   

.. function:: mkdirat(dirfd, pathname[, mode=0777])

    Create a new directory.
    Behaves in a manner similar to :func:`os.mkdir`.

    If pathname is relative then the directory will be created relative to
    the directory referred to by the directory file descriptor *dirfd*.


.. function:: mkfifoat(dirfd, pathname[, mode=0666])

    Create a FIFO (named pipe).
    Behaves in a manner similar to :func:`os.mkfifo`.

    If pathname is relative then the file will be created relative to
    the directory referred to by the directory file descriptor *dirfd*.


.. function:: mknodat(dirfd, pathname[, mode=0600][, device=0])

    Create a file system node.
    Behaves in a manner similar to :func:`os.mknod`.

    If pathname is relative then the file will be created relative to
    the directory referred to by the directory file descriptor *dirfd*.


.. function:: openat(dirfd, pathname[, flags][, mode=0600])

    Opens a file returning a file descriptor (integer).
    Behaves in a manner similar to :func:`os.open`.
    Flags accepts the same flags as :func:`os.open` including
    any of the additional O_* flags exposed by this module.

    If pathname is relative then the file will be opened relative to
    the directory referred to by the directory file descriptor *dirfd*.

   
.. function:: readlinkat(dirfd, pathname)

    Return the path that a symbolic link points to. 
    Behaves in a manner similar to :func:`os.readlink`.

    If pathname is relative then the link is read relative to
    the directory referred to by the directory file descriptor *dirfd*.
   

.. function:: renameat(oldfd, oldpath, newfd, newpath)

    Rename a file from the "old location" to the "new location".
    Behaves in a manner similar to :func:`os.rename`.

    If either oldpath or newpath is relative then the file being renamed
    is relative the directory referred to by the the directory file
    descriptor preceding it.
   

.. function:: symlinkat(source, dirfd, pathname)

    Create a symbolic link pointing to the path indicated by source.
    Behaves in a manner similar to :func:`os.symlink`.

    If pathname is relative then the file is removed relative to
    the directory referred to by the directory file descriptor *dirfd*.
   

.. function:: unlinkat(dirfd, pathname[, flags])

    Unlinks/removes a file in the file system. Behaves in a manner
    similar to :func:`os.unlink`.

    If pathname is relative then the file is removed relative to
    the directory referred to by the directory file descriptor *dirfd*.
    Specifying the :const:`AT_REMOVEDIR` flag will cause the function
    to remove directories instead of files, similar to :func:`os.rmdir`. 


.. function:: utimensat(dirfd, pathname, (atime, mtime))

    Set the access and modified times on a file with nanosecond
    precision. Behaves in a manner similar to :func:`os.utime`.
    
    The time tuple may be given as a single None value to set both
    atime and mtime to the current time. Otherwise, atime and mtime
    must both be either an integer, a float, or a two-tuple containing
    the time value in seconds followed by a value in nanoseconds.

    If pathname is relative then the file is modified relative to
    the directory referred to by the directory file descriptor *dirfd*.



Constants
-------------

.. data:: HAVE_FUTIMESAT
          HAVE_UTIMENSAT

    Boolean values that will be set to true if the underlying library
    call is present on this system.


.. data:: AT_FDCWD

   This value can be specified as the *dirfd* (directory file descriptor)
   argument. When this is done the pathname is interpreted as 
   relative to the current working directory of the process, making the
   calls behave similarly to the calls minus the `*at` suffix.


.. data:: AT_EACCESS

   Flag used to indicate that access checks should be done 
   using the effective user and group IDs. May be ORed with other flags.


.. data:: AT_SYMLINK_NOFOLLOW

   Flag used to indicate that the call must *not* follow symlinks.
   May be ORed with other flags.


.. data:: AT_REMOVEDIR

   Flag used to indicate that the call will remove directories
   instead of file objects. May be ORed with other flags.


.. data:: O_CLOEXEC

   Flag that can be passed to open calls like :const:`O_TRUNC` or
   :const:`O_RDONLY`. It will cause the file descriptor to be closed
   automatically if the process exec's.
   This call is only available on some platforms.


.. _d_type constants:

.. data:: DT_UNKNOWN
          DT_BLK
          DT_CHR
          DT_DIR
          DT_FIFO
          DT_LNK
          DT_REG
          DT_SOCK

    These values correspond to a file system object type, except for 
    DT_UNKNOWN which indicates that the type could not be determined.
    File systems that do not support d_type will always return DT_UNKNOWN
    (equivalent to zero).

    The remaining values are for block devices, character devices,
    directories, fifo (named pipe) files, symbolic links, 
    regular files, and socket files respectively.


.. data:: FSLIB_INCL_DTYPE

    This flag customizes the output of directory listing functions
    like :func:`listdir` and :func:`fdlistdir` so that the results
    include d_type values.




.. _time-of-check to time-of-use errors: https://en.wikipedia.org/wiki/Time_of_check_to_time_of_use
