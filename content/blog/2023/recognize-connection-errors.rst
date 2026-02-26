Recognize connection errors
###########################

:date: 2023-03-16
:tags: python, socket, network

Lately I've been dealing with an asynchronous TCP client app which sends
messages to a remote server. Some of these messages are important, and cannot
get lost. Because the connection may drop at any time, I had to implement a
mechanism to resend the message once the client reconnects. As such, I needed
a way to identify what constitutes a **connection error**.

Python provides a builtin ConnectionError_ exception precisely for this
purpose, but it turns out it's not enough. After observing logs in production,
I found some errors that were not related to the socket connection per se, but
rather to the **system connectivity**, like `ENETUNREACH`
("network unreachable") or `ENETDOWN` ("network down").  It's interesting to
note how this distinction is reflected in the UNIX errno_  code prefixes:
`ECONN*` (connection errors) vs. `ENET*` (network errors). I've noticed
`ENET*` errors usually occur on a DHCP renewal, or more in general when the
Wi-Fi signal is weak or absent. Because this code runs on a cleaning robot
which constantly moves around the house, connection can become unstable when
the robot gets far from the Wi-Fi Access Point, so it's pretty common to bump
into errors like these:

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

Production logs also revealed a considerable amount of SSL-related errors. I
was uncertain what to do about those. The app is supposed to gracefully handle
them, so theoretically they should represent a bug. Still, they are
unequivocally related to the connection stream, and represent a failed attempt
to send data, so we want to retry it. Example of logs I found:

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
of these cases I came up with this solution which I think is worth sharing, as
it's generic enough to be reused in similar situations. If needed, this can be
easily extended to include specific exceptions of third party libraries, like
`requests.exceptions.ConnectionError`.

.. code-block:: python

    """
    Recognize a connection error from an exception object.
    Author: Giampaolo Rodola
    License: MIT
    """

    import errno, socket, ssl

    import botocore.exceptions
    import requests.exceptions

    # Network errors, usually related to DHCP or wpa_supplicant (Wi-Fi).
    NETWORK_ERRNOS = frozenset((
        errno.ENETUNREACH,  # "Network is unreachable"
        errno.ENETDOWN,  # "Network is down"
        errno.ENETRESET,  # "Network dropped connection on reset"
        errno.ENONET,  # "Machine is not on the network"
        errno.ENOTCONN,  # "Transport endpoint is not connected"
        errno.EBADF,  # "Bad file descriptor"
    ))

    # requests lib connection errors
    REQUESTS_EXCEPTIONS = (
        requests.exceptions.ConnectionError,
        requests.exceptions.ProxyError,
        requests.exceptions.SSLError,
        requests.exceptions.Timeout,
        requests.exceptions.ConnectTimeout,
        requests.exceptions.ReadTimeout,
        requests.exceptions.ChunkedEncodingError,
    )

    # botocore lib connection errors
    BOTOCORE_EXCEPTIONS = (
        botocore.exceptions.ConnectionClosedError,
        botocore.exceptions.ConnectionError,
        botocore.exceptions.ConnectTimeoutError,
        botocore.exceptions.EndpointConnectionError,
        botocore.exceptions.ReadTimeoutError,
        botocore.exceptions.SSLError,
    )


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
            # Timeout on connect(), recv(), send().
            return True
        if isinstance(exc, OSError):
            if exc.errno in NETWORK_ERRNOS:
                return True
        if isinstance(exc, ssl.SSLError):
            # Let's consider any SSL error a connection error. Usually this is:
            # * ssl.SSLZeroReturnError: "TLS/SSL connection has been closed"
            # * ssl.SSLError: [SSL: BAD_LENGTH]
            return True
        if isinstance(exc, REQUESTS_EXCEPTIONS):
            # Any indication that requests lib failed due to a connection
            # error.
            return True
        if isinstance(exc, BOTOCORE_EXCEPTIONS):
            # Any indication that boto3 lib failed due to a connection
            # error.
            return True
        return False


    # =====================================================================
    # --- unit tests
    # =====================================================================

    import unittest


    class TestIsConnectionErr(unittest.TestCase):
        def test_connection_error(self):
            for exc in (
                BrokenPipeError(),
                ConnectionAbortedError(),
                ConnectionRefusedError(),
                ConnectionResetError(),
            ):
                assert is_connection_err(exc)

        def test_not_connection_error(self):
            assert not is_connection_err(ValueError())
            assert not is_connection_err(OSError())
            assert not is_connection_err(Exception())

        def test_requests_exceptions(self):
            for exc in (
                requests.exceptions.ConnectionError(),
                requests.exceptions.Timeout(),
                requests.exceptions.SSLError(),
            ):
                assert is_connection_err(exc)

        def test_botocore_exceptions(self):
            for exc in (
                botocore.exceptions.ConnectionClosedError(endpoint_url="x"),
                botocore.exceptions.ConnectTimeoutError(endpoint_url="x"),
                botocore.exceptions.ReadTimeoutError(endpoint_url="x"),
            ):
                assert is_connection_err(exc)


    if __name__ == "__main__":
        unittest.main()

To use it:

.. code-block:: python

    try:
        sock.sendall(b"hello there")
    except Exception as err:
        if is_connection_err(err):
            schedule_on_reconnect(lambda: sock.sendall(b"hello there"))
        raise

External Links
--------------

* Github Gist_

.. _ConnectionError: https://docs.python.org/3/library/exceptions.html#ConnectionError
.. _errno: https://www.thegeekstuff.com/2010/10/linux-error-codes/
.. _Gist: https://gist.github.com/giampaolo/905b38a5ea9d5179eb0138e2f37a01a8
