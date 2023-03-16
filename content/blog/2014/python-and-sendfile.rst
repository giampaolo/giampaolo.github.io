Python and sendfile
###################

:date: 2014-06-13
:tags: python, python-dev, sendfile, zerocopy, network, recipe, socket

`sendfile(2) <http://linux.die.net/man/2/sendfile>`__ is a UNIX system call which provides a "zero-copy" way of copying data from one file descriptor (a file) to another (a socket). Because this copying is done entirely within the kernel, `sendfile(2)` is more efficient than the combination of `file.read()` and `socket.send()`, which requires transferring data to and from user space.  This copying of the data twice imposes some performance and resource penalties which `sendfile(2)` syscall avoids; it also results in a single system call (and thus only one context switch), rather than the series of `read(2) <http://linux.die.net/man/2/read>`__ / `write(2) <http://linux.die.net/man/2/write>`__ system calls (each system call requiring a context switch) used internally for the data copying. A more exhaustive explanation of how `sendfile(2)` works is available `here <http://www.techrepublic.com/article/use-sendfile-to-optimize-data-transfer/>`__, but long story short is that sending a file with `sendfile()` is usually `twice as fast <https://github.com/giampaolo/pysendfile#a-simple-benchmark>`__ than using plain `socket.send() <https://docs.python.org/3/library/socket.html#socket.socket.send>`__. Typical applications which can benefit from using `sendfile()` are FTP and HTTP servers.

socket.sendfile()
-----------------

I recently contributed a patch for Python's socket module which adds a high-level `socket.sendfile() <https://docs.python.org/3.5/library/socket.html#socket.socket.sendfile>`__ method (see full discussion at `BPO-17552 <http://bugs.python.org/issue17552>`__). `socket.sendfile()` will transmit a file until EOF is reached by attempting to use `os.sendfile() <https://docs.python.org/3/library/os.html#os.sendfile>`__, if available, else it falls back on using plain `socket.send()`. Internally, it takes care of handling socket timeouts and provides two optional parameters to move the file offset or to send only a limited amount of bytes. I came up with this idea because getting all of that right is a bit tricky, so a generic wrapper seemed to be convenient to have. `socket.sendfile()` will make its appearance in Python 3.5.

sendfile and Python
-------------------

`sendfile(2)` made its first appearance into the Python stdlib kind of late: Python 3.3. It was contributed by Ross Lagerwall and me in `BPO-10882 <http://bugs.python.org/issue10882>`__. Since the patch didn't make it into python 2.X and I wanted to `use sendfile() in pyftpdlib <https://code.google.com/p/pyftpdlib/issues/detail?id=152>`__ I later decided to release it as a stand alone module working with older (2.5+) Python versions (see `pysendfile <https://github.com/giampaolo/pysendfile>`__ project). Starting with version 3.5, Python will hopefully start using `sendfile()` more extensively, in details:

* `BPO-13563: ftplib <http://bugs.python.org/issue13564>`__
* `BPO-13559: httplib <http://bugs.python.org/issue13559>`__
* asyncio: there are some plans for this even though no actual patch yet, see `discussion <https://groups.google.com/d/msg/python-tulip/i4OHlIkExsA/eqaK5fzEfCAJ>`__ and `BDFL involvement <http://bugs.python.org/issue17552#msg217099>`__.

Also, Windows provides something similar to sendfile(2): `TransmitFile <http://msdn.microsoft.com/en-us/library/windows/desktop/ms740565(v=vs.85).aspx>`__. Now that socket.sendfile() is in place it seems natural to add support for it as well (see `BPO-21721 <http://bugs.python.org/issue21721>`__).

Backport to Python 2.6 and 2.7
------------------------------

For those of you who are interested in using `socket.sendfile()` with older Python 2.6 and 2.7 versions here's a backport. It requires `pysendfile <https://github.com/giampaolo/pysendfile>`__ module to be installed. Full code including tests is hosted `here <https://code.activestate.com/recipes/578889-socketsendfile/>`__.

.. code-block:: python

    #!/usr/bin/env python

    """
    This is a backport of socket.sendfile() for Python 2.6 and 2.7.
    socket.sendfile() will be included in Python 3.5:
    http://bugs.python.org/issue17552
    Usage:

    >>> import socket
    >>> file = open("somefile.bin", "rb")
    >>> sock = socket.create_connection(("localhost", 8021))
    >>> sendfile(sock, file)
    42319283
    >>>
    """

    import errno
    import io
    import os
    import select
    import socket
    try:
        memoryview  # py 2.7 only
    except NameError:
        memoryview = lambda x: x

    if os.name == 'posix':
        import sendfile as pysendfile  # requires "pip install pysendfile"
    else:
        pysendfile = None


    _RETRY = frozenset((errno.EAGAIN, errno.EALREADY, errno.EWOULDBLOCK,
                        errno.EINPROGRESS))


    class _GiveupOnSendfile(Exception):
        pass


    if pysendfile is not None:

        def _sendfile_use_sendfile(sock, file, offset=0, count=None):
            _check_sendfile_params(sock, file, offset, count)
            sockno = sock.fileno()
            try:
                fileno = file.fileno()
            except (AttributeError, io.UnsupportedOperation) as err:
                raise _GiveupOnSendfile(err)  # not a regular file
            try:
                fsize = os.fstat(fileno).st_size
            except OSError:
                raise _GiveupOnSendfile(err)  # not a regular file
            if not fsize:
                return 0  # empty file
            blocksize = fsize if not count else count

            timeout = sock.gettimeout()
            if timeout == 0:
                raise ValueError("non-blocking sockets are not supported")
            # poll/select have the advantage of not requiring any
            # extra file descriptor, contrarily to epoll/kqueue
            # (also, they require a single syscall).
            if hasattr(select, 'poll'):
                if timeout is not None:
                    timeout *= 1000
                pollster = select.poll()
                pollster.register(sockno, select.POLLOUT)

                def wait_for_fd():
                    if pollster.poll(timeout) == []:
                        raise socket._socket.timeout('timed out')
            else:
                # call select() once in order to solicit ValueError in
                # case we run out of fds
                try:
                    select.select([], [sockno], [], 0)
                except ValueError:
                    raise _GiveupOnSendfile(err)

                def wait_for_fd():
                    fds = select.select([], [sockno], [], timeout)
                    if fds == ([], [], []):
                        raise socket._socket.timeout('timed out')

            total_sent = 0
            # localize variable access to minimize overhead
            os_sendfile = pysendfile.sendfile
            try:
                while True:
                    if timeout:
                        wait_for_fd()
                    if count:
                        blocksize = count - total_sent
                        if blocksize <= 0:
                            break
                    try:
                        sent = os_sendfile(sockno, fileno, offset, blocksize)
                    except OSError as err:
                        if err.errno in _RETRY:
                            # Block until the socket is ready to send some
                            # data; avoids hogging CPU resources.
                            wait_for_fd()
                        else:
                            if total_sent == 0:
                                # We can get here for different reasons, the main
                                # one being 'file' is not a regular mmap(2)-like
                                # file, in which case we'll fall back on using
                                # plain send().
                                raise _GiveupOnSendfile(err)
                            raise err
                    else:
                        if sent == 0:
                            break  # EOF
                        offset += sent
                        total_sent += sent
                return total_sent
            finally:
                if total_sent > 0 and hasattr(file, 'seek'):
                    file.seek(offset)
    else:
        def _sendfile_use_sendfile(sock, file, offset=0, count=None):
            raise _GiveupOnSendfile(
                "sendfile() not available on this platform")


    def _sendfile_use_send(sock, file, offset=0, count=None):
        _check_sendfile_params(sock, file, offset, count)
        if sock.gettimeout() == 0:
            raise ValueError("non-blocking sockets are not supported")
        if offset:
            file.seek(offset)
        blocksize = min(count, 8192) if count else 8192
        total_sent = 0
        # localize variable access to minimize overhead
        file_read = file.read
        sock_send = sock.send
        try:
            while True:
                if count:
                    blocksize = min(count - total_sent, blocksize)
                    if blocksize <= 0:
                        break
                data = memoryview(file_read(blocksize))
                if not data:
                    break  # EOF
                while True:
                    try:
                        sent = sock_send(data)
                    except OSError as err:
                        if err.errno in _RETRY:
                            continue
                        raise
                    else:
                        total_sent += sent
                        if sent < len(data):
                            data = data[sent:]
                        else:
                            break
            return total_sent
        finally:
            if total_sent > 0 and hasattr(file, 'seek'):
                file.seek(offset + total_sent)


    def _check_sendfile_params(sock, file, offset, count):
        if 'b' not in getattr(file, 'mode', 'b'):
            raise ValueError("file should be opened in binary mode")
        if not sock.type & socket.SOCK_STREAM:
            raise ValueError("only SOCK_STREAM type sockets are supported")
        if count is not None:
            if not isinstance(count, int):
                raise TypeError(
                    "count must be a positive integer (got %s)" % repr(count))
            if count <= 0:
                raise ValueError(
                    "count must be a positive integer (got %s)" % repr(count))


    def sendfile(sock, file, offset=0, count=None):
        """sendfile(sock, file[, offset[, count]]) -> sent

        Send a *file* over a connected socket *sock* until EOF is
        reached by using high-performance sendfile(2) and return the
        total number of bytes which were sent.
        *file* must be a regular file object opened in binary mode.
        If sendfile() is not available (e.g. Windows) or file is
        not a regular file socket.send() will be used instead.
        *offset* tells from where to start reading the file.
        If specified, *count* is the total number of bytes to transmit
        as opposed to sending the file until EOF is reached.
        File position is updated on return or also in case of error in
        which case file.tell() can be used to figure out the number of
        bytes which were sent.
        The socket must be of SOCK_STREAM type.
        Non-blocking sockets are not supported.
        """
        try:
            return _sendfile_use_sendfile(sock, file, offset, count)
        except _GiveupOnSendfile:
            return _sendfile_use_send(sock, file, offset, count)
