

fsnix.util - Higher Level Tools
========================================

.. module:: fsnix.util
    :synopsis: Higher Level API using fslib calls


Module API
-----------------

.. function:: setfdcloexec(fd)

    Set the file descriptor to be automatically closed if
    the process exec's. Returns fd.
    This is a convenience function wrapping fcntl module calls.


.. function:: closingfd(fd)

    Context manager that automatically calls :func:`os.close` on the
    fd. Behaves in a similar manner to :func:`contextlib.closing`,
    but for file descriptors instead of file objects.


.. function:: removeall(dirfd, path, errback=None, _fs=None)

    Recursively delete a file or directory tree indicated by
    path (relative to directory file descriptor *dirfd*).
    Similar in intent to :func:`shutil.rmtree` but is more
    robust in the face of symlink attack.

    If *errback* is specified it must be a callable that accepts
    the arguments (error, path). Error will be the exception
    encountered and path is the object being deleted.
    The *_fs* argument allows the user to pass in a custom "fslib"
    module if needed.


.. function:: opendir(path)

    Return a :class:`directory` object corresponding to the specified
    *path*.


.. function:: fdopendir(dirfd)
    
    Return a :class:`directory` object corresponding to already
    opened directory file descriptor *dirfd*.
    

.. function:: opendirat(dirfd, path, _fs=None)

    Return a :class:`directory` object corresponding to the specified
    directory file descriptor *dirfd* and *path*.

    The *_fs* argument allows the user to pass in a custom "fslib"
    module if needed.
    

.. function:: walk(top, topdown=True, onerror=None, followlinks=False, _fs=None)

    An alternate implementation of :func:`os.walk` which demonstrates
    the use of some of the lower level :mod:`fslib` functions.

    .. note:: *followlinks* is not supported by this function.
    

Directory Objects
-------------------

You should not try to instantiate a directory object directly. Instead,
use :func:`opendir`, :func:`opendirat`, or :func:`fdopendir`.


.. class:: directory

    Directory objects are intended to mimic the API of Python file objects
    to a limited degree. They are context managers and support the fileno
    method to get the file descriptor value. Instead of supporting IO
    methods some simple directory listing wrappers are supported.

    .. attribute:: name

       The path name of the directory, or None if not available.

    .. attribute:: closed

       A boolean indicating that the directory has been closed.

    .. method:: fileno()
    
        Return the value of the open file descriptor for this directory.
        If you get confused and want to make sure you are using a
        directory object `dirno` is available as an alias to fileno.

    .. method:: close()

        Closes the directory.

    .. method:: listdir(_fs=None)

        Return a list of entries in the open directory.
        Specify *_fs* if you need to use an alternate fslib module.

