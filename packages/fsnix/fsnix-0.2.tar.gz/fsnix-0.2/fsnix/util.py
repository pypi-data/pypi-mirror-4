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
"""util - A grab bag of file system level tools

Functions and classes that using the openat and friends but providing
a higher level interface.
"""

from fsnix import fs

import os
import stat
import fcntl


__all__ = [
    'setfdcloexec',
    'closingfd',
    'removeall',
    'opendir',
    'fdopendir',
    'opendirat',
    'walk',
    ]


def getfs(customfs=None):
    """Return custom fs namespace (if it is not None) or
    default fs namespace.
    This allows you to provide custom implemenation or
    wrapped versions of file operations
    """
    if customfs is None:
        return fs
    else:
        return customfs


def setfdcloexec(fd):
    """Wrapper function that sets the given fd to CLOEXEC using fcntl.
    This will cause the file descriptor to be closed upon exec'ing.
    (See man fcntl for more details)
    Returns the given fd
    """
    fcntl.fcntl(fd, fcntl.F_SETFD, fcntl.FD_CLOEXEC)
    return fd


class closingfd(object):
    """A context manager that will execute os.close on the
    given fd upon exit. Returns the fd when entered.
    """

    def __init__(self, fd):
        self.fd = fd

    def __enter__(self):
        return self.fd

    def __exit__(self, etype, exc, tb):
        os.close(self.fd)
        return


def removeall(fd, path, errback=None, _fs=None):
    """Similar to shutil.rmtree only it requires a directory fd
    and path element to remove. Will unlink path if it is a file,
    or remove it recursively if it is a dir.
    """
    _fs = getfs(_fs)
    try:
        statres = _fs.fstatat(fd, path, _fs.AT_SYMLINK_NOFOLLOW)
        is_dir = stat.S_ISDIR(statres.st_mode)
    except OSError, err:
        if errback:
            errback(err, path)
            return
        else:
            raise
    try:
        if not is_dir:
            _fs.unlinkat(fd, path)
        else:
            flags = os.O_RDONLY | os.O_DIRECTORY
            with closingfd(_fs.openat(fd, path, flags)) as dfd:
                setfdcloexec(dfd)
                dentries = _fs.fdlistdir(os.dup(dfd))
                for dentry in dentries:
                    removeall(dfd, dentry, _fs)
            _fs.unlinkat(fd, path, _fs.AT_REMOVEDIR)
    except (OSError, IOError), err:
        if errback:
            errback(err, path)
        else:
            raise


def opendir(path):
    """Return a directory object for the given path.
    """
    flags = (os.O_RDONLY | os.O_DIRECTORY)
    if fs.O_CLOEXEC:
        # if O_CLOEXEC is available use it: prevents race conditions
        # in threaded applications
        flags |= fs.O_CLOEXEC
        fd = os.open(path, flags)
    else:
        fd = setfdcloexec(os.open(path, flags))
    return directory(fd, path)


def fdopendir(dirfd):
    """Return a directory object for a given directory fd.
    """
    return directory(dirfd, '<fdopendir>')


def opendirat(dirfd, path, _fs=None):
    """Returns a directory object given an dirfd and path .
    """
    _fs = getfs(_fs)
    flags = (os.O_RDONLY | os.O_DIRECTORY)
    if fs.O_CLOEXEC:
        flags |= fs.O_CLOEXEC
        nfd = _fs.openat(dirfd, path, flags)
    else:
        nfd = setfdcloexec(_fs.openat(dirfd, path, flags))
    return directory(nfd, path)


class directory(object):
    """An object representing a directory handle.
    Can be used as a context manager, that closes the dir handle on exit.
    Supports the fileno function (returning an fd) like file objects.
    """
    __slots__ = ('_dirfd', '_open', '_name')

    def __init__(self, dirfd, name=None):
        if not isinstance(dirfd, int):
            raise ValueError('not an integer (file descriptor)')
        self._dirfd = dirfd
        self._name = name
        self._open = True

    def fileno(self):
        if self.closed:
            raise ValueError('I/O operation on closed directory')
        return self._dirfd

    # alias fileno to dirno
    dirno = fileno

    def close(self):
        """Close the open directory handle"""
        if self._open:
            os.close(self._dirfd)
            self._open = False

    def __enter__(self):
        """Enter the ctx manager - returns itself"""
        return self

    def __exit__(self, errtype, errval, errtb):
        """Exit the ctx manager, closing the handle"""
        self.close()

    @property
    def closed(self):
        """Returns true if handle is closed"""
        return not self._open

    @property
    def name(self):
        """Returns handle name/path"""
        return self._name

    def listdir(self, _fs=None):
        """Return directory contents in a list for current handle.
        """
        _fs = getfs(_fs)
        return _fs.fdlistdir(os.dup(self._dirfd))


def walk(top, topdown=True, onerror=None, followlinks=False, _fs=None):
    if followlinks:
        raise NotImplementedError('followlinks is not supported'
                                  ' - all symlinks are treated as files')

    _fs = getfs(_fs)
    j = os.path.join
    try:
       dirents = _fs.listdir(top, _fs.FSLIB_INCL_DTYPE)
    except os.error, err:
        if onerror is not None:
            onerror(err)
        return

    d, f = [], []
    for name, dtype in dirents:
        if dtype == _fs.DT_UNKNOWN:
            s = os.lstat(j(top, name))
            is_dir = stat.S_ISDIR(s.st_mode)
            if is_dir:
                d.append(name)
            else:
                f.append(name)
        elif dtype == _fs.DT_DIR:
            d.append(name)
        else:
            f.append(name)

    if topdown:
        yield (top, d, f)
    for name in d:
        newtop = j(top, name)
        for x in walk(newtop, topdown, onerror, followlinks, _fs):
            yield x
    if not topdown:
        yield (top, d, f)
