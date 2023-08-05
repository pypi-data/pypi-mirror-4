.. fsnix documentation master file, created by
   sphinx-quickstart on Fri Oct  7 13:03:20 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=====================================
fsnix: file system API for Python 2.x
=====================================

Introduction
-------------

This library provides modules for Python 2.x that expose some of the
useful File System related API calls, including some of those added
in POSIX.1-2008. This includes the functions openat, mkdirat, unlinkat,
and other similar calls suffixed
with "at". These calls exist to help defend against race conditions and
support thread-level working directories. Typically these functions take
one or more directory file descriptor and a relative path as arguments.
This library also comes with custom directory listing functions that
mimic os.listdir by default but can provide additional information
(d_type) when passed a flag. Similarly, file descriptor and iterator
based versions are also available.

Additionally, this library provides a util module that has a higher level
interface for working with open directories and other functions that
use the lower level library calls.


Examples
-----------

Open a directory, and create a file in that directory, then remove it.

>>> import tempfile, os
>>> from fsnix import fs
>>> root = tempfile.mkdtemp()
>>> dirfd = os.open(root, os.O_RDONLY)
>>> fd = fs.openat(dirfd, "foobar.txt", os.O_CREAT | os.O_RDWR)
>>> os.write(fd, "Hello World\n")
12
>>> os.close(fd)
>>> os.listdir(root)
['foobar.txt']
>>> fs.unlinkat(dirfd, 'foobar.txt')
>>> os.close(dirfd)
>>> os.listdir(root)
[]


This example shows how to create a subdirectory, write a file into that and
then rename the directory, all using the low-level APIs.

>>> import tempfile, os
>>> from fsnix import fs
>>> root = tempfile.mkdtemp()
>>> dirfd = os.open(root, os.O_RDONLY)
>>> fs.mkdirat(dirfd, 'ham')
>>> dirfd2 = fs.openat(dirfd, 'ham', os.O_RDONLY)
>>> os.close(fs.openat(dirfd2, "foobar.txt", os.O_CREAT | os.O_RDWR))
>>> os.close(dirfd2)
>>> fs.renameat(dirfd, 'ham', dirfd, 'bacon')
>>> os.close(dirfd)
>>> os.listdir(os.path.join(root, 'bacon'))
['foobar.txt']

The util module aims at providing a higher level interface to make some
common actions simpler. This example tries to wipe out any empty directories
in the example directory.

>>> import tempfile, os, errno
>>> from fsnix import fs
>>> from fsnix import util
>>> root = tempfile.mkdtemp()
>>> for i in range(0, 19):
...     if i & 1:
...         open(os.path.join(root, str(i)), 'w').close()
...     else:
...         os.mkdir(os.path.join(root, str(i)))
>>> open(os.path.join(root, '0', 'foo'), 'w').close()
>>> with util.opendir(root) as dh:
...     for name in dh.listdir():
...         try:
...             fs.unlinkat(dh.fileno(), name, fs.AT_REMOVEDIR)
...         except OSError, e:
...             if e.errno != errno.ENOTDIR and e.errno != errno.ENOTEMPTY:
...                 raise
>>> sorted(os.listdir(root), key=int)
['0', '1', '3', '5', '7', '9', '11', '13', '15', '17']


Compatibility
-------------

The API for the POSIX.1-2008 `*at` functions mimic those found in
the C library. For the 3.3 release the developers of the Python
Standard Library combined these functions with the existing
versions in the `os` module. However, the underlying functionality
is provided by the same APIs that fslib exposes directly.
(I have considered adding another module that would provide a similar
API to that of the Python Standard Library but have not done the work yet.
The fslib module will always continue to expose the lower level API directly.)

The listdir-like functions should behave similarly to os.listdir when
not passed any flags. The extended listdir calls are designed only to
vary where appropriate.

I am currently testing against Linux and FreeBSD. Specifically,
Fedora 14 and up and FreeBSD 9.0. If you think the module should work
on your platform and it does not, please report a bug. Please be aware
that I do not have access to proprietary/esoteric platforms. This module
will not work on Windows systems.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

