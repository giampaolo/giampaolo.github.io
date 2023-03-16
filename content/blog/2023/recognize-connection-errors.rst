Recognize connection errors
###########################

:date: 2023-03-16
:tags: python, socket, network

Lately I've been dealing with an asynchronous TCP client app which sends
messages to a remote server. Some of these messages are important, and cannot
get lost. Because the connection may drop at any time, I was asked to
implement a mechanism to resend the message once the client reconnects. As
such, I needed a way to identify what constitutes a **connection error**.

Python provides a builtin ConnectionError_ exception precisely for this
purpose, but it turns out it's not enough. After observing logs in production,
I found some errors that were not related to the socket connection per se, but
rather to the **system connectivity**, like `ENETUNREACH`
("network unreachable") or `ENETDOWN` ("network down").  It's interesting to
note how this distinction is reflected in the UNIX errno_  code prefixes:
`ECONN*` (connection errors) vs. `ENET*` (network errors). I've noticed
`ENET*` errors usually occur on a DHCP renewal, or more in general when the
Wi-Fi signal is weak or absent. Because this code runs on a moving cleaning
robot connected to the Wi-Fi, connection may become unstable when the robot
gets far from the Access Point, so it's pretty common to bump into one these:

::

    File "/usr/lib/python3.7/ssl.py", line 934, in send
        return self._sslobj.write(data)
    OSError: [Errno 101] Network is unreachable

    File "/usr/lib/python3.7/socket.py", line 222, in getaddrinfo
        for res in _socket.getaddrinfo(host, port, family, type, proto, flags):
    socket.gaierror: [Errno -3] Temporary failure in name resolution

    File "/usr/lib/python3.7/ssl.py", line 934, in send
        return self._sslobj.write(data)
    BrokenPipeError: [Errno 32] Broken pipe

    File "/usr/lib/python3.7/ssl.py", line 934, in send
        return self._sslobj.write(data)
    socket.timeout: The write operation timed out

Production logs revealed a considerable amount of SSL-related errors as well. I
was uncertain what to do about those. The app is supposed to gracefully handle
them, so theoretically they should represent a bug. Still, they are
unequivocally related to the connection stream, and represent a failed
attempt to send data that we want to retry. Example of logs I found:

::

    File "/usr/lib/python3.7/ssl.py", line 934, in send
        return self._sslobj.write(data)
    ssl.SSLZeroReturnError: TLS/SSL connection has been closed (EOF)

    File "/usr/lib/python3.7/ssl.py", line 934, in send
        return self._sslobj.write(data)
    ssl.SSLError: [SSL: BAD_LENGTH] bad length

Looking at production logs revealed what sort of brutal, rough and tumble place
the Internet is, and how a network app must be ready to handle all sorts of
unexpected error conditions which hardly show up during testing. To handle all
of these cases, I came up with this solution, which I think is worth sharing
as it's generic enough to be reused in similar situations:

.. code-block:: python

    import errno, socket, ssl

    # Network errors, usually related to DHCP or wpa_supplicant (Wi-Fi).
    NETWORK_ERRNOS = frozenset((
        errno.ENETUNREACH,  # "Network is unreachable"
        errno.ENETDOWN,  # "Network is down"
        errno.ENETRESET,  # "Network dropped connection on reset"
        errno.ENONET,  # "Machine is not on the network"
    ))

    def is_connection_err(exc):
        """Return True if an exception is connection-related."""
        if isinstance(exc, ConnectionError):
            # https://docs.python.org/3/library/exceptions.html#ConnectionError
            # ConnectionError includes:
            # * BrokenPipeError (EPIPE, ESHUTDOWN)
            # * ConnectionAbortedError (ECONNABORTED)
            # * ConnectionRefusedError (ECONNREFUSED)
            # * ConnectionResetError (ECONNRESET)
            return True
        if isinstance(exc, socket.gaierror):
            # failed DNS resolution on connect()
            return True
        if isinstance(exc, (socket.timeout, TimeoutError)):
            # timeout on connect(), recv(), send()
            return True
        if isinstance(exc, OSError):
            # ENOTCONN == "Transport endpoint is not connected"
            return (exc.errno in NETWORK_ERRNOS) or (exc.errno == errno.ENOTCONN)
        if isinstance(exc, ssl.SSLError):
            # Let's consider any SSL error a connection error. Usually this is:
            # * ssl.SSLZeroReturnError: "TLS/SSL connection has been closed"
            # * ssl.SSLError: [SSL: BAD_LENGTH] bad length
            return True
        return False

To use it:

.. code-block:: python

    try:
        sock.sendall(b"hello there")
    except Exception as err:
        if is_connection_err(err):
            schedule_on_reconnect(lambda: sock.sendall(b"hello there"))
        raise

.. _ConnectionError: https://docs.python.org/3/library/exceptions.html#ConnectionError
.. _errno: https://www.thegeekstuff.com/2010/10/linux-error-codes/
