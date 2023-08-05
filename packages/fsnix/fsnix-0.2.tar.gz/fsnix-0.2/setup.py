#!/usr/bin/env python

from distutils.core import setup, Extension
import distutils.ccompiler
import os

DEBUG = False

DIST = {
    'name': 'fsnix',
    'version': '0.2',
    'description': 'Expose new or advanced posix/file system APIs to Python',
    'author': 'John Mulligan',
    'author_email': 'phlogistonjohn@asynchrono.us',
    'classifiers': [
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: BSD :: FreeBSD',
        'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: System :: Filesystems',
        'License :: OSI Approved :: MIT License'],
}


# -- dynamic structure --

# apparently the built in has_function in distutils is broken
# and leaves a.out files behind, and fails to clean up after
# itself. Running a check that should fail after a successful check
# gives a incorrect result of success.
#
def has_function(cc, funcname):
    import tempfile, shutil
    tmpdir = tempfile.mkdtemp()
    cfile = os.path.join(tmpdir, 'test.c')
    aout = os.path.join(tmpdir, 'a.out')
    success = False
    try:
        fh = open(cfile, 'w')
        fh.write('int main(void) {\n  %s();\n}\n' % funcname)
        fh.close()
        try:
            objects = cc.compile([cfile], output_dir=tmpdir)
            cc.link_executable(objects, aout)
            success = True
        except Exception:
            pass
    finally:
        shutil.rmtree(tmpdir)
    return success


def detect_feature_macros():
    fflags = {}
    cc = distutils.ccompiler.new_compiler()
    if has_function(cc, 'futimesat'):
        fflags['HAVE_FUTIMESAT'] = 1
    if has_function(cc, 'utimensat'):
        fflags['HAVE_UTIMENSAT'] = 1
    return [(k, v) for k, v in fflags.items()]


extflags = {}
extflags['define_macros'] = detect_feature_macros()
if DEBUG:
    extflags['extra_compile_args'] = '-O0 -ggdb'.split()

PACKAGE = {
    'packages': ['fsnix'],
    'ext_modules': [
        Extension('fsnix.fslib', ['fsnix/fslib.c'], **extflags),
    ]
}


if __name__ == '__main__':
    options = {}
    options.update(DIST)
    options.update(PACKAGE)
    setup(**options)
