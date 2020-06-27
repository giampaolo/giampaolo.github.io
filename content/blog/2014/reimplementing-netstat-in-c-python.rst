Reimplementing netstat in Python
################################

:date: 2014-03-10
:tags: python, network

`psutil <https://github.com/giampaolo/psutil/>`__ 2.1.0 is out and with it I finally managed to implement something I've been wanting to have for a long time: netstat-like functionalities (see `ticket <https://code.google.com/p/psutil/issues/detail?id=387>`__). Similarly to `"netstat -antp"` on UNIX you can now list system-wide connections in pure python and also determine **what process (PID) is using a particular connection**:

.. code-block:: python

    >>> import psutil
    >>> from pprint import pprint as pp
    >>> pp(psutil.net_connections())
    [sconn(fd=-1, family=2, type=1, laddr=('127.0.0.1', 587), raddr=(), status='LISTEN', pid=None),
     sconn(fd=-1, family=2, type=1, laddr=('127.0.0.1', 6379), raddr=(), status='LISTEN', pid=None),
     sconn(fd=-1, family=2, type=1, laddr=('127.0.1.1', 53), raddr=(), status='LISTEN', pid=None),
     sconn(fd=-1, family=2, type=1, laddr=('10.0.3.1', 53), raddr=(), status='LISTEN', pid=None),
     sconn(fd=-1, family=2, type=1, laddr=('127.0.0.1', 631), raddr=(), status='LISTEN', pid=None),
     sconn(fd=-1, family=2, type=1, laddr=('127.0.0.1', 25), raddr=(), status='LISTEN', pid=None),
     sconn(fd=-1, family=2, type=1, laddr=('0.0.0.0', 3389), raddr=(), status='LISTEN', pid=None),
     sconn(fd=17, family=2, type=1, laddr=('127.0.0.1', 34785), raddr=(), status='LISTEN', pid=3591),
     sconn(fd=15, family=2, type=1, laddr=('127.0.0.1', 56359), raddr=(), status='LISTEN', pid=3591),
     sconn(fd=-1, family=10, type=2, laddr=('::', 56720), raddr=(), status='NONE', pid=None)]
    >>>

This is yet another functionality which can be used for monitoring purposes. For example, say you want to make sure your HTTP server is running on port 80, you can do something like this:

.. code-block:: python

    import psutil

    def check_listening_port(port):
        """Return True if the given TCP port is busy and in LISTEN mode."""
        for conn in psutil.net_connections(kind='tcp'):
            if conn.laddr[1] == port and conn.status == psutil.CONN_LISTEN:
                return True
        return False

    print(check_listening_port(80))

Netstat in pure python
----------------------

Here it is, in 65 lines of code: `netstat.py <https://github.com/giampaolo/psutil/blob/master/scripts/netstat.py>`__. Pretty neat right? ;-)

Implementation(s)
-----------------

As always, each platform required its own, different, implementation. Luckily for some platforms (OSX, Windows) I was able to reuse and customize some code from the existing `Process.connections()` implementation which was already in place. For those of you who are interested in knowing how this was done here's the source code references:

* `Linux <https://github.com/giampaolo/psutil/blob/6242f7411b882d525e5d267de4bcda1079934ea2/psutil/_pslinux.py#L741>`__
* `Windows <https://github.com/giampaolo/psutil/blob/6242f7411b882d525e5d267de4bcda1079934ea2/psutil/arch/windows/socks.c>`__
* `FreeBSD <https://github.com/giampaolo/psutil/blob/6242f7411b882d525e5d267de4bcda1079934ea2/psutil/arch/freebsd/sys_socks.c>`__
* `Solaris <https://github.com/giampaolo/psutil/blob/6242f7411b882d525e5d267de4bcda1079934ea2/psutil/_psutil_sunos.c#L1115>`__
* `OSX <https://github.com/giampaolo/psutil/blob/6242f7411b882d525e5d267de4bcda1079934ea2/psutil/_psutil_osx.c#L1072>`__

Hopefully this will help whoever needs to do this into another language. The only platform where this is sort of clunky is OSX, which does not expose anything to list all system-wide sockets in a single shot, so you're forced to query each process. That means you'll need root privileges otherwise you'll get an access denied error. For what it's worth, I took a look at `lsof` and it has the same limitation and netstat runs with SUID. Well, I guess this is it. I'll leave you with `some docs <https://psutil.readthedocs.io/en/latest/#psutil.net_connections>`__. For the next one I'm planning on working on a couple of other network-related functionalities: `"ifconfig" <https://code.google.com/p/psutil/issues/detail?id=376>`__ and `NIC speeds <https://code.google.com/p/psutil/issues/detail?id=250>`__. But that's for another time...
