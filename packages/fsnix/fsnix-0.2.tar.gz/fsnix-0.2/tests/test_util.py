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
"""Test fsnix.util module
"""

import unittest
import shutil
import tempfile

import os
import errno
import time
import string
import random
import threading

from fsnix import fs
from fsnix import util


class TestFsnixUtil(unittest.TestCase):

    def setUp(self):
        self.tdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tdir)
        self.tdir = None

    def wfile(self, dirn, filen, content):
        with open(os.path.join(dirn, filen), 'wb') as fh:
            fh.write(content)

    def test_directory_opendir(self):
        dirh = util.opendir(self.tdir)
        self.assertTrue(dirh.fileno() > 1)
        with dirh:
            l = dirh.listdir()
        self.assertEqual(l, [])
        self.assertEqual(dirh.closed, True)
        self.wfile(self.tdir, 'foo', '12345\n')
        self.wfile(self.tdir, 'bar', '54321\n')
        self.wfile(self.tdir, 'baz', '')
        with util.opendir(self.tdir) as dirh2:
            self.assertEqual(dirh2.name, self.tdir)
            l = dirh.listdir()
        l.sort()
        self.assertEqual(l, ['bar', 'baz', 'foo'])
        self.assertRaises(OSError, dirh2.listdir)
        self.assertRaises(ValueError, dirh2.dirno)

    def test_directory_fdopendir(self):
        dirh = util.fdopendir(os.open(self.tdir, os.O_RDONLY))
        self.assertTrue(dirh.fileno() > 1)
        with dirh:
            l = dirh.listdir()
        self.assertEqual(l, [])
        self.assertEqual(dirh.closed, True)
        self.wfile(self.tdir, 'foo', '12345\n')
        self.wfile(self.tdir, 'bar', '54321\n')
        self.wfile(self.tdir, 'baz', '')
        fd2 = os.open(self.tdir, os.O_RDONLY)
        with util.fdopendir(fd2) as dirh2:
            self.assertEqual(dirh2.name, '<fdopendir>')
            l = dirh.listdir()
        l.sort()
        self.assertEqual(l, ['bar', 'baz', 'foo'])
        self.assertRaises(OSError, dirh2.listdir)

    def test_directory_fdopendirat(self):
        t2 = os.path.join(self.tdir, 'kablam')
        os.mkdir(t2)
        self.wfile(t2, 'foo', '12345\n')
        self.wfile(t2, 'bar', '54321\n')
        self.wfile(t2, 'baz', '')
        with util.opendir(self.tdir) as dirh:
            with util.opendirat(dirh.fileno(), 'kablam', fs) as dirh2:
                l = dirh2.listdir()
            l.sort()
            self.assertEqual(l, ['bar', 'baz', 'foo'])
            self.assertRaises(OSError, dirh2.listdir)

    def test_cloexec_wrapper(self):
        self.wfile(self.tdir, 'foo', '12345\n')
        with open(os.path.join(self.tdir, 'foo'), 'w') as fh:
            util.setfdcloexec(fh.fileno())

    def test_closingfd(self):
        fd = os.open(os.path.join(self.tdir, 'zapp'), os.O_RDWR | os.O_CREAT)
        with util.closingfd(fd):
            os.write(fd, 'fooooooo\n')
        self.assertRaises(OSError, os.write, fd, 'baar\n')
        with open(os.path.join(self.tdir, 'zapp')) as fh:
            self.assertEqual(fh.read(), 'fooooooo\n')

    def test_removeall_simple(self):
        t1 = os.path.join(self.tdir, 'INNER')
        os.mkdir(t1)
        d, f = gen_tree(t1)
        self.assertEqual(len(d) + len(f), 100)
        self.assertEqual(os.listdir(self.tdir), ['INNER'])
        with util.opendir(self.tdir) as dh:
            util.removeall(dh.fileno(), 'INNER')
        self.assertEqual(os.listdir(self.tdir), [])

    def test_removeall_attack(self):
        good = tempfile.mkdtemp(dir=self.tdir)
        evil = tempfile.mkdtemp(dir=self.tdir)
        tmp = '%s_1' % good
        fnum = 1 << 16

        for ii in xrange(fnum):
            open(os.path.join(good, 'g%d' % ii), 'wb').close()
            open(os.path.join(evil, 'e%d' % ii), 'wb').close()
        self.assertEqual(len(os.listdir(good)), fnum)
        self.assertEqual(len(os.listdir(evil)), fnum)

        class Attack(threading.Thread):
            daemon = 1
            def run(self):
                time.sleep(0.25)
                os.rename(good, tmp)
                os.symlink(evil, good)
        Attack().start()

        #shutil.rmtree(good, True)
        with util.opendir(self.tdir) as dh:
            try:
                util.removeall(dh.fileno(), os.path.basename(good))
            except OSError, err:
                if err.errno != errno.ENOTDIR:
                    raise
        self.assertTrue(os.path.isdir(evil))
        self.assertEqual(len(os.listdir(evil)), fnum)
        self.assertEqual(os.listdir(tmp), [])


def gen_tree(rootdir):
    dirs, files = [rootdir], []
    for ii in range(0, 99):
        what = random.choice([dirs, files])
        container = random.choice(dirs)
        name = gen_name()
        path = os.path.join(container, name)
        if what is dirs:
            dirs.append(path)
            os.mkdir(path)
        else:
            files.append(path)
            with open(path, 'wb') as fh:
                for jj in range(0, 10):
                    fh.write('%s\n' % gen_name())
    return dirs, files


def gen_name(s=(string.letters + string.digits + '_-')):
    size = random.choice(range(1, 26))
    return ''.join(random.sample(s, size))


if __name__ == '__main__':
    unittest.main()
