Reimplementing ifconfig in Python
#################################

:date: 2015-06-13
:tags: psutil, python, personal, new-api, compatibility, featured, release
:slug: psutil-30-reimplement-ifconfig-in-python

Here we are. It's been a long time since my last blog post and my last `psutil <https://github.com/giampaolo/psutil>`__ release. The reason? I've been travelling! I mean... a lot. I've spent 3 months in Berlin, 3 weeks in Japan and 2 months in New York City. While I was there I finally had the chance to meet my friend `Jay Loden <http://jayloden.com/software.htm>`__ in person. We originally started working on psutil together `7 years ago <https://groups.google.com/forum/#!topic/psutil-dev/fj8DQ3lGFH4>`__.

.. raw:: html

    <div>
        <a href="/images/me-with-jay.jpg">
        <img src="/images/me-with-jay.jpg" style="width:750px; height:500px" />
        </a>
    </div>

Back then I didn't know any C (and I'm still a terrible C developer), so he was crucial in developing the initial psutil skeleton, including macOS and Windows support. Needless to say that this release builds on that work.

net_if_addrs()
--------------

We're now able to list network interface addresses similarly to the ``ifconfig`` command on UNIX:

.. code-block:: pycon

    >>> import psutil
    >>> from pprint import pprint
    >>> pprint(psutil.net_if_addrs())
    {'ethernet0': [snic(family=<AddressFamily.AF_INET: 2>,
                        address='10.0.0.4',
                        netmask='255.0.0.0',
                        broadcast='10.255.255.255'),
                   snic(family=<AddressFamily.AF_PACKET: 17>,
                        address='9c:eb:e8:0b:05:1f',
                        netmask=None,
                        broadcast='ff:ff:ff:ff:ff:ff')],
     'localhost': [snic(family=<AddressFamily.AF_INET: 2>,
                        address='127.0.0.1',
                        netmask='255.0.0.0',
                        broadcast='127.0.0.1'),
                   snic(family=<AddressFamily.AF_PACKET: 17>,
                        address='00:00:00:00:00:00',
                        netmask=None,
                        broadcast='00:00:00:00:00:00')]}

This is limited to ``AF_INET`` (IPv4), ``AF_INET6`` (IPv6) and ``AF_LINK`` (Ethernet) address families. If you want something more powerful (e.g. ``AF_BLUETOOTH``) you can take a look at the `netifaces <https://pypi.python.org/pypi/netifaces/>`__ extension. If you want to see how this is implemented, here's the code for POSIX and Windows:

* `POSIX <https://github.com/giampaolo/psutil/blob/39161251010503d6b087807c473f4fb648dfcbce/psutil/_psutil_posix.c#L151>`__
* `Windows <https://github.com/giampaolo/psutil/blob/39161251010503d6b087807c473f4fb648dfcbce/psutil/_psutil_windows.c#L2907>`__

net_if_stats()
--------------

This new function returns information about network interface cards:

.. code-block:: pycon

    >>> import psutil
    >>> from pprint import pprint
    >>> pprint(psutil.net_if_stats())
    {'ethernet0': snicstats(isup=True,
                            duplex=<NicDuplex.NIC_DUPLEX_FULL: 2>,
                            speed=100,
                            mtu=1500),
     'localhost': snicstats(isup=True,
                            duplex=<NicDuplex.NIC_DUPLEX_UNKNOWN: 0>,
                            speed=0,
                            mtu=65536)}

The implementation on each platform:

* `Windows <https://github.com/giampaolo/psutil/blob/39161251010503d6b087807c473f4fb648dfcbce/psutil/_psutil_windows.c#L3057>`__
* `Linux <https://github.com/giampaolo/psutil/blob/39161251010503d6b087807c473f4fb648dfcbce/psutil/_psutil_linux.c#L474>`__
* `macOS & FreeBSD <https://github.com/giampaolo/psutil/blob/39161251010503d6b087807c473f4fb648dfcbce/psutil/_psutil_posix.c#L229>`__
* `SunOS <https://github.com/giampaolo/psutil/blob/39161251010503d6b087807c473f4fb648dfcbce/psutil/_psutil_sunos.c#L1153>`__

Also in 3.0
-----------

Beyond the network-interface APIs, psutil 3.0 ships a few other notable changes.

Several integer/string constants (``IOPRIO_CLASS_*``, ``NIC_DUPLEX_*``, ``*_PRIORITY_CLASS``) now return ``enum`` values on Python 3.4+.

Support for zombie processes on UNIX was broken. Covered in a `separate post <zombie-processes>`_.

Removal of deprecated APIs
--------------------------

All aliases deprecated in the `psutil 2.0 porting guide <../2014/psutil-20-api-redesign>`_ (January 2014) are gone. For the full list see the `changelog <https://psutil.readthedocs.io/en/latest/#id23>`__.

Final words
-----------

I must say I'm pretty satisfied with how psutil is evolving and with the enjoyment I still get every time I work on it. It now gets almost `800,000 downloads a month <https://pypi.python.org/pypi/psutil#downloads>`__, which is quite remarkable for a Python library.

At this point, I consider psutil almost "complete" feature-wise, meaning I'm starting to run out of ideas for what to add next (see `TODO <https://github.com/giampaolo/psutil/blob/v3.0.0/TODO>`__). Going forward, development will likely focus on supporting more exotic platforms (`OpenBSD #562 <https://github.com/giampaolo/psutil/issues/562>`__, `NetBSD PR-557 <https://github.com/giampaolo/psutil/pull/557>`__, `Android #355 <https://github.com/giampaolo/psutil/issues/355>`__).

There have also been discussions on the python-ideas mailing list about `including psutil in the Python stdlib <https://mail.python.org/pipermail//python-ideas/2014-October/029835.html>`__, but even if that happens, it's still a long way off, as it would require a significant time investment that I currently don't have.
