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
"""fsnix - utility library for file system APIs

There are two modules within this library called fslib and fswlib,
the former uses the Python C-API and the latter uses ctypes. The
first one available will be aliased in under the name 'fs'.

fslib is more complete but requires compilation. fswlib is less complete
(see documenation for details) but works w/o a compiler available.
"""


USING_LIB = None
try:
    from fsnix import fslib as fs
    USING_LIB = 'fslib'
except ImportError:
    pass

if not USING_LIB:
    try:
        from fsnix import fswlib as fs
        USING_LIB = 'fswlib'
    except ImportError:
        pass
