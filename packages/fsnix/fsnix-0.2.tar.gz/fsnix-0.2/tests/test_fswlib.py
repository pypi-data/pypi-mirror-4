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
"""Test fswlib module (fs wrapped library)
"""

import unittest
import shutil
import tempfile

import os
import errno
import stat
import time
import contextlib

from fsnix import fswlib


class TestPosixPlus(unittest.TestCase):

    def setUp(self):
        self.tdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tdir)
        self.tdir = None

    def opentdir(self):
        return os.open(self.tdir, os.O_DIRECTORY)

    @contextlib.contextmanager
    def getdir(self):
        dirfd = self.opentdir()
        try:
            yield dirfd
        finally:
            os.close(dirfd)

    def assertRaisesErrno(self, exc, errno, func, *args, **kwargs):
        try:
            v = func(*args, **kwargs)
            caught_exc = None
        except Exception, err:
            caught_exc = err
        test = type(caught_exc) is exc
        assert test, "failed to catch exception: %s" % exc
        test = (errno == caught_exc.errno)
        assert test, "errno: %r != %r" % (errno, caught_exc.errno)

    # tests

    def test_openat(self):
        fd = os.open(self.tdir, os.O_DIRECTORY)
        fd2 = None
        txt = 'HELLO WORLD\n'
        try:
            assert type(fd) is int, 'fd is not an int'
            fd2 = fswlib.openat(fd, 'test1.txt', os.O_CREAT|os.O_RDWR)
            os.write(fd2, txt)
        finally:
            if fd: os.close(fd)
            if fd2: os.close(fd2)
        ptest = os.path.join(self.tdir, 'test1.txt')
        with open(ptest) as fp:
            self.assertEqual(fp.read(), txt)

    def test_openat_mode(self):
        os.umask(0)
        fd = os.open(self.tdir, os.O_DIRECTORY)
        fd2 = None
        txt = 'HELLO FARM\n'
        try:
            fd2 = fswlib.openat(fd, 'test2.txt',
                    os.O_CREAT|os.O_RDWR, 0664)
            os.write(fd2, txt)
        finally:
            if fd: os.close(fd)
            if fd2: os.close(fd2)
        ptest = os.path.join(self.tdir, 'test2.txt')
        with open(ptest) as fp:
            self.assertEqual(fp.read(), txt)
        sr = os.stat(ptest)
        self.assertEqual(oct(stat.S_IMODE(sr.st_mode)), oct(0664))


    def test_openat_existing(self):
        ptest = os.path.join(self.tdir, 'test3.txt')
        txt = 'A\nB\nC\n'
        with open(ptest, 'w') as fp:
            fp.write(txt)
        dirfd = os.open(self.tdir, os.O_DIRECTORY)
        fd2 = None
        try:
            fd2 = fswlib.openat(dirfd, 'test3.txt', os.O_RDONLY)
            contents = os.read(fd2, 1024)
        finally:
            if dirfd: os.close(dirfd)
            if fd2: os.close(fd2)
        self.assertEqual(txt, contents)


    def test_unlinkat(self):
        ptest = os.path.join(self.tdir, 'junk.txt')
        txt = 'A\nB\nC\n'
        with open(ptest, 'w') as fp:
            fp.write(txt)
        dirfd = self.opentdir()
        try:
            fswlib.unlinkat(dirfd, 'junk.txt')
        finally:
            if dirfd: os.close(dirfd)


    def test_unlinkat_rmdir(self):
        ptest = os.path.join(self.tdir, 'mumbo.d')
        os.mkdir(ptest)
        assert 'mumbo.d' in os.listdir(self.tdir)
        dirfd = self.opentdir()
        try:
            fswlib.unlinkat(dirfd, 'mumbo.d', fswlib.AT_REMOVEDIR)
        finally:
            os.close(dirfd)
        assert 'mumbo.d' not in os.listdir(self.tdir)


    def test_unlinkat_missing(self):
        assert 'mumbo.d' not in os.listdir(self.tdir)
        dirfd = self.opentdir()
        try:
            self.assertRaises(OSError,
                    fswlib.unlinkat,
                    dirfd, 'mumbo.d', fswlib.AT_REMOVEDIR)
        finally:
            os.close(dirfd)
        assert 'mumbo.d' not in os.listdir(self.tdir)


    def test_faccessat(self):
        p1 = os.path.join(self.tdir, 'foo.txt')
        with open(p1, 'w') as fh:
            fh.write('AAAAAAAAAAAAAAA\n')
        with self.getdir() as dfd:
            self.assertTrue(
                fswlib.faccessat(dfd, 'foo.txt', os.R_OK))
            self.assertTrue(
                fswlib.faccessat(dfd, 'foo.txt', os.W_OK))
        os.chmod(p1, 0400)
        with self.getdir() as dfd:
            self.assertTrue(
                fswlib.faccessat(dfd, 'foo.txt', os.R_OK))
            self.assertFalse(
                fswlib.faccessat(dfd, 'foo.txt', os.W_OK))

    def test_faccessat_eaccess_flag(self):
        p1 = os.path.join(self.tdir, 'foo.txt')
        with open(p1, 'w') as fh:
            fh.write('AAAAAAAAAAAAAAA\n')
        with self.getdir() as dh:
            self.assertTrue(
                fswlib.faccessat(dh, 'foo.txt', os.R_OK,
                                    fswlib.AT_EACCESS))
            self.assertTrue(
                fswlib.faccessat(dh, 'foo.txt', os.W_OK,
                                    fswlib.AT_EACCESS))

    def test_fchmodat(self):
        os.umask(0)
        p1 = os.path.join(self.tdir, 'crummy')
        with open(p1, 'w') as fh:
            fh.write('0000000\n')
        with self.getdir() as dh:
            fswlib.fchmodat(dh, 'crummy', 0600)
        self.assertEqual(0600,
                stat.S_IMODE(os.stat(p1).st_mode))
        with self.getdir() as dh:
            fswlib.fchmodat(dh, 'crummy', 0604)
        self.assertEqual(0604,
                stat.S_IMODE(os.stat(p1).st_mode))

    # FIXME - something is goofy here
    def test_fchownat(self):
        if os.getuid() != 0:
            return self.fchownat_lame()
        else:
            assert False, 'whoa there, I havent tested as root yet'

    def fchownat_lame(self):
        """this one only sets the uid/gid to the uid gid it was created
        with. Stupid but pretty much always works w/o trying to do
        lots of overhead.
        """
        p1 = os.path.join(self.tdir, 'bw1')
        with open(p1, 'w') as fh:
            fh.write('whoop\n')
        u, g = os.getuid(), os.getgid()
        os.chown(p1, u, g)
        with self.getdir() as dh:
            fswlib.fchownat(dh, 'bw1', u, g)
        s1 = os.stat(p1)
        self.assertEqual(s1.st_uid, u)
        self.assertEqual(s1.st_gid, g)

    def NIMPL_fstatat(self):
        p1 = os.path.join(self.tdir, 'yak.txt')
        with open(p1, 'w') as fh:
            fh.write('foobar\nbaz\n')
        with self.getdir() as dh:
            s1 = fswlib.fstatat(dh, 'yak.txt')
        s2 = os.stat(p1)
        self.assertEqual(s1.st_mode, s2.st_mode)
        self.assertEqual(s1.st_uid, s2.st_uid)
        self.assertEqual(s1.st_ino, s2.st_ino)
        self.assertEqual(s1.st_size, s2.st_size)
        self.assertTrue(stat.S_ISREG(s1.st_mode))


    def NIMPL_fstatat_symlink(self):
        p1 = os.path.join(self.tdir, 'real.txt')
        p2 = os.path.join(self.tdir, 'fake.txt')
        with open(p1, 'w') as fh:
            fh.write('abcde\n01234\n')
        os.symlink(p1, p2)
        with self.getdir() as dh:
            s1 = fswlib.fstatat(dh, 'fake.txt')
            s2 = fswlib.fstatat(dh, 'fake.txt',
                               fswlib.AT_SYMLINK_NOFOLLOW)
        # s1 points at the linked file
        self.assertTrue(stat.S_ISREG(s1.st_mode))
        self.assertFalse(stat.S_ISLNK(s1.st_mode))
        # s2 points at the link itself
        self.assertFalse(stat.S_ISREG(s2.st_mode))
        self.assertTrue(stat.S_ISLNK(s2.st_mode))


    def test_linkat(self):
        p1 = os.path.join(self.tdir, 'x1.txt')
        p2 = os.path.join(self.tdir, 'x2.txt')
        with open(p1, 'w') as fh:
            fh.write('XXXXXXXXXXXXXXXXXX\n');
            fh.write('xxxxxxxxxxxxxxxxxx\n');

        with self.getdir() as dfd:
            fswlib.linkat(dfd, 'x1.txt',
                         dfd, 'x2.txt')
        s1 = os.stat(p1)
        s2 = os.stat(p2)
        self.assertEqual(s1.st_nlink, 2)
        self.assertEqual(s1.st_ino, s2.st_ino)

    def test_mkdirat(self):
        p1 = os.path.join(self.tdir, 'crummy')
        self.assertRaises(OSError, os.listdir, p1)
        with self.getdir() as dfd:
            fswlib.mkdirat(dfd, 'crummy')
        self.assertEqual(os.listdir(p1), [])


    def test_mknodat(self):
        fswlib.mknodat

    def test_readlinkat(self):
        p1 = os.path.join(self.tdir, 'blah.lnk')
        os.symlink('/dev/null', p1)
        with self.getdir() as dh:
            pth = fswlib.readlinkat(dh, 'blah.lnk')
        self.assertEqual(pth, '/dev/null')

    def test_renameat(self):
        p1 = os.path.join(self.tdir, 'mambo.dat')
        with open(p1, 'w') as fh:
            fh.write('ALPHA\nBETA\nGAMMA\n')
        self.assertEqual(os.listdir(self.tdir), ['mambo.dat'])
        with self.getdir() as dfd:
            fswlib.renameat(dfd, 'mambo.dat',
                           dfd, 'salsa.txt')
        self.assertEqual(os.listdir(self.tdir), ['salsa.txt'])
        with open(os.path.join(self.tdir, 'salsa.txt')) as fh:
            self.assertEqual(fh.read(), 'ALPHA\nBETA\nGAMMA\n')


    def test_symlinkat(self):
        p1 = os.path.join(self.tdir, 'zero_carbs')
        with self.getdir() as dfd:
            fswlib.symlinkat('/dev/null', dfd, 'zero_carbs')
        lnk = os.readlink(p1)
        self.assertEqual(lnk, '/dev/null')

    def NIMPL_utimensat(self):
        p1 = os.path.join(self.tdir, 'clock-work')
        with open(p1, 'w') as fh:
            fh.write('ALPHA\nBETA\nGAMMA\n')
        t1 = 903535.52
        t2 = 12313234
        t3 = (900900, 6300)
        with self.getdir() as dh:
            fswlib.utimensat(dh, 'clock-work', (t1, t1))
            self.assertEqual(int(t1),
                int(os.stat(p1).st_mtime))
            fswlib.utimensat(dh, 'clock-work', (t2, t2))
            self.assertEqual(t2,
                int(os.stat(p1).st_atime))
            fswlib.utimensat(dh, 'clock-work', (t3, t3))
            self.assertEqual(t3[0],
                int(os.stat(p1).st_mtime))
            fswlib.utimensat(dh, 'clock-work', None)
            self.assertEqual(int(time.time()),
                int(os.stat(p1).st_mtime))

    def NIMPL_futimesat(self):
        p1 = os.path.join(self.tdir, 'clock-work')
        with open(p1, 'w') as fh:
            fh.write('ALPHA\nBETA\nGAMMA\n')
        t1 = 903535.52
        t2 = 12313234
        t3 = (900900, 6300)
        with self.getdir() as dh:
            fswlib.futimesat(dh, 'clock-work', (t1, t1))
            self.assertEqual(int(t1),
                int(os.stat(p1).st_mtime))
            fswlib.futimesat(dh, 'clock-work', (t2, t2))
            self.assertEqual(t2,
                int(os.stat(p1).st_atime))
            fswlib.futimesat(dh, 'clock-work', (t3, t3))
            self.assertEqual(t3[0],
                int(os.stat(p1).st_mtime))
            fswlib.futimesat(dh, 'clock-work', None)
            self.assertEqual(int(time.time()),
                int(os.stat(p1).st_mtime))

    def test_mkfifoat(self):
        os.umask(0)
        p1 = os.path.join(self.tdir, 'fido')
        with self.getdir() as dh:
            fswlib.mkfifoat(dh, 'fido')
        s1 = os.stat(p1)
        self.assertTrue(stat.S_ISFIFO(s1.st_mode))
        self.assertEqual(stat.S_IMODE(s1.st_mode), 0666)
        os.unlink(p1)
        with self.getdir() as dh:
            fswlib.mkfifoat(dh, 'fido', 0600)
        s1 = os.stat(p1)
        self.assertTrue(stat.S_ISFIFO(s1.st_mode))
        self.assertEqual(stat.S_IMODE(s1.st_mode), 0600)

    def test_fdlistdir(self):
        f1 = os.path.join(self.tdir, 'antelope')
        f2 = os.path.join(self.tdir, 'bear')
        f3 = os.path.join(self.tdir, 'copperhead')
        with open(f1, 'w') as fh:
            fh.write('foo\n')
        with open(f2, 'w') as fh:
            fh.write('bar\n')
        with open(f3, 'w') as fh:
            fh.write('baz\n')
        with self.getdir() as dh:
            dlist = fswlib.fdlistdir(os.dup(dh))
        dlist.sort()
        self.assertEqual(dlist, ['antelope', 'bear', 'copperhead'])

    def test_fdlistdir_badfd(self):
        with self.getdir() as dh:
            tempdh = os.dup(dh)
            os.close(tempdh)
            self.assertRaises(OSError, fswlib.fdlistdir, tempdh)
        f1 = os.path.join(self.tdir, 'antelope')
        with open(f1, 'w') as fh:
            self.assertRaises(OSError, fswlib.fdlistdir, tempdh)

    def test_fdlistdir_inthread(self):
        f1 = os.path.join(self.tdir, 'antelope')
        f2 = os.path.join(self.tdir, 'bear')
        f3 = os.path.join(self.tdir, 'copperhead')
        with open(f1, 'w') as fh:
            fh.write('foo\n')
        with open(f2, 'w') as fh:
            fh.write('bar\n')
        with open(f3, 'w') as fh:
            fh.write('baz\n')
        res = []
        def foo():
            with self.getdir() as dh:
                dlist = fswlib.fdlistdir(os.dup(dh))
            res.extend(dlist)
            res.sort()
        import threading
        t = threading.Thread(target=foo)
        t.daemon = True
        t.start()
        t.join()
        self.assertEqual(res, ['antelope', 'bear', 'copperhead'])

    def test_fditerdir(self):
        import select
        f1 = os.path.join(self.tdir, 'antelope')
        f2 = os.path.join(self.tdir, 'bear')
        f3 = os.path.join(self.tdir, 'copperhead')
        with open(f1, 'w') as fh:
            fh.write('foo\n')
        with open(f2, 'w') as fh:
            fh.write('bar\n')
        with open(f3, 'w') as fh:
            fh.write('baz\n')
        with self.getdir() as dh:
            d2 = os.dup(dh)
            diriter = fswlib.fditerdir(d2)
            select.select([d2], [], [])
            dlist = []
            dlist.append(diriter.next())
            dlist.append(diriter.next())
            dlist.append(diriter.next())
            self.assertRaises(StopIteration, diriter.next)
            dlist.sort()
            self.assertEqual(dlist, ['antelope', 'bear', 'copperhead'])
            # do it again
            select.select([dh], [], [])
            diriter = fswlib.fditerdir(d2)
            select.select([d2], [], [])
            dlist = []
            dlist.append(diriter.next())
            dlist.append(diriter.next())
            dlist.append(diriter.next())
            self.assertRaises(StopIteration, diriter.next)
            dlist.sort()
            self.assertEqual(dlist, ['antelope', 'bear', 'copperhead'])
            os.close(d2)
            self.assertRaises(select.error, select.select, [d2], [], [])
            self.assertRaises(OSError, fswlib.fditerdir, d2)

    def test_fditerdir_closeearly(self):
        import select
        import gc
        f1 = os.path.join(self.tdir, 'antelope')
        f2 = os.path.join(self.tdir, 'bear')
        f3 = os.path.join(self.tdir, 'copperhead')
        for fn in [f1, f2, f3]:
            with open(fn, 'w') as fh:
                fh.write('foo\n')
        with self.getdir() as dh:
            d2 = os.dup(dh)
            with fswlib.fditerdir(d2) as diriter:
                self.assertTrue(diriter.next() in ['antelope', 'bear', 'copperhead'])
            self.assertRaises(StopIteration, diriter.next)

            items = []
            diriter = fswlib.fditerdir(d2)
            items.append(diriter.next())
            os.close(d2)
            self.assertRaises(select.error, select.select, [d2], [], [])
            items.append(diriter.next())
            items.append(diriter.next())
            self.assertRaises(StopIteration, diriter.next)


    def test_flags(self):
        fswlib.AT_FDCWD
        fswlib.AT_REMOVEDIR
        fswlib.AT_SYMLINK_NOFOLLOW
        fswlib.AT_EACCESS


if not fswlib.HAVE_UTIMENSAT:
    print 'disabling utimensat test'
    TestPosixPlus.test_utimensat = None
if not fswlib.HAVE_FUTIMESAT:
    print 'disabling futimesat test'
    TestPosixPlus.test_futimesat = None


if __name__ == '__main__':
    unittest.main()
