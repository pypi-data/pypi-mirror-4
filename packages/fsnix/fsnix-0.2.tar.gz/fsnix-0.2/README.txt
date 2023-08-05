
=======================================
fsnix - Modern File System APIs & Such
=======================================

This library is designed to expose various file and file system related
APIs for modern POSIX compatible systems to Python. This includes
functions that wrap openat and other *at type calls (from POSIX.1-2008)
that are not available for Python 2.x. In addition it provides a stdlib
compatible listdir call which can also be used to return d_type values
from a directory entry on file systems that support that feature.

This package provides 'fsnix.fslib' which is the compiled module that
provides the "full" low-level api. The module 'fsnix.fswlib' is a
ctypes wrapper that tracks fslib where possible and can be used where
you can not use a C compiler. Finally 'fslib.util' provides some
convenient, higher-level, more pythonic interfaces that use the other
modules.


API Stability
--------------

I consider API stability an important part of any library. This
becomes more and more important as a new library matures is used
by more people. The fsnix.fslib module is the core of the library
and maintained with the intent of keeping backwards compatibility
in mind, however until 1.0 I do not plan on being backwards
compatible where I think I've made a design mistake.
The fsnix.fswlib module should follow that as it shadows the
functionality of fslib but using ctypes. The API of the 
fslib.util module is still immature and can fluctuate
between versions.


* Current Version: 0.2
* License: MIT License

