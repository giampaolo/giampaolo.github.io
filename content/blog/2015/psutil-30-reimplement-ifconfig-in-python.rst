psutil 3.0, aka how I reimplemented ifconfig in Python
######################################################

:date: 2015-06-13
:tags: psutil, travel, personal

Here we are. It's been a long time since my last blog post and my last `psutil <https://github.com/giampaolo/psutil>`__ release. The reason? I've been travelling! I mean... a lot. I've spent 3 months in Berlin, 3 weeks in Japan and 2 months in New York City. While I was there I finally had the chance to meet my friend `Jay Loden <http://jayloden.com/software.htm>`__ in person. `Jay and I <https://fbcdn-sphotos-h-a.akamaihd.net/hphotos-ak-xta1/t31.0-8/11263024_10153285412879890_759604551146752808_o.jpg>`__ originally started working on psutil together `7 years ago <https://groups.google.com/forum/#!topic/psutil-dev/fj8DQ3lGFH4>`__.

.. raw:: html

    <div>
        <a href="/images/me-with-jay.jpg">
        <img src="/images/me-with-jay.jpg" style="width:750px; height:500px" />
        </a>
    </div>


Back then I didn't know any C (and I still am a terrible C developer) so he's been crucial to develop the initial psutil skeleton including OSX and Windows support. I'm back home now (but not for long ;-)), so I finally have some time to write this blog post and tell you about the new psutil release. Let's see what happened.

net_if_addrs()
--------------

In a few words, we're now able to list network interface addresses similarly to "ifconfig" command on UNIX:

.. code-block:: python

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

This is limited to AF_INET (IPv4), AF_INET6 (IPv6) and AF_LINK (ETHERNET) address families. If you want something more poweful (e.g. AF_BLUETOOTH) you can take a look at `netifaces <https://pypi.python.org/pypi/netifaces/>`__ extension. And here's the code which does these tricks on POSIX and Windows:

* `POSIX <https://github.com/giampaolo/psutil/blob/39161251010503d6b087807c473f4fb648dfcbce/psutil/_psutil_posix.c#L151>`__
* `Windows <https://github.com/giampaolo/psutil/blob/39161251010503d6b087807c473f4fb648dfcbce/psutil/_psutil_windows.c#L2907>`__

Also, here's some `doc <https://psutil.readthedocs.io/en/latest/#psutil.net_if_addrs>`__.

net_if_stats()
--------------

This will return a bunch of information about network interface cards:

.. code-block:: python

    >>> import psutil
    >>> from pprint import pprint
    >>> pprint(psutil.net_if_stats())
    {'ethernet'0: snicstats(isup=True,
                            duplex=<NicDuplex.NIC_DUPLEX_FULL: 2>,
                            speed=100,
                            mtu=1500),
     'localhost': snicstats(isup=True,
                            duplex=<NicDuplex.NIC_DUPLEX_UNKNOWN: 0>,
                            speed=0,
                            mtu=65536)}

Again, here's the code for each platform:

* `Windows <https://github.com/giampaolo/psutil/blob/39161251010503d6b087807c473f4fb648dfcbce/psutil/_psutil_windows.c#L3057>`__
* `Linux <https://github.com/giampaolo/psutil/blob/39161251010503d6b087807c473f4fb648dfcbce/psutil/_psutil_linux.c#L474>`__
* `OSX & FreeBSD <https://github.com/giampaolo/psutil/blob/39161251010503d6b087807c473f4fb648dfcbce/psutil/_psutil_posix.c#L229>`__
* `SunOS <https://github.com/giampaolo/psutil/blob/39161251010503d6b087807c473f4fb648dfcbce/psutil/_psutil_sunos.c#L1153>`__

...and the `doc <https://psutil.readthedocs.io/en/latest/#psutil.net_if_stats>`__.

Enums
-----

`Enums <https://docs.python.org/3/library/enum.html>`__ are a nice new feature introduced in Python 3.4. Very briefly (or at least, this is what I appreciate the most about them), they help you write an API with human-readable constants. If you use Python 2 you'll see something like this:

.. code-block:: python

    >>> import psutil
    >>> psutil.IOPRIO_CLASS_IDLE
    3

On Python 3.4 you'll see a more informative:

.. code-block:: python

    >>> import psutil
    >>> psutil.IOPRIO_CLASS_IDLE
    <IOPriority.IOPRIO_CLASS_IDLE: 3>

They are backward compatible, meaning if you're sending serialized data produced with psutil through the network you can safely use comparison operators and so on. The psutil APIs returning enums (on Python >=3.4) are:

* psutil.net_connections() (the address families):
* psutil.Process.connections() (same as above)
* psutil.net_if_stats()  (all ``NIC_DUPLEX_*`` constants)
* psutil.Process.nice() on Windows (for all the ``*_PRIORITY_CLASS`` constants)
* psutil.Process.ionice() on Linux (for all the ``IOPRIO_CLASS_*`` constants)

All the other existing constants remained plain strings (``STATUS_*``) or integers (``CONN_*``).

Zombie processes
----------------

This is a big one. The full story is `here <https://github.com/giampaolo/psutil/issues/428>`__ but basically the support for `zombie processes <http://askubuntu.com/a/48625>`__ on UNIX was `broken <https://github.com/giampaolo/psutil/issues/428>`__ (except on Linux, and Windows doesn't have zombie processes). Up until psutil 2.X we could instantiate a zombie process:

.. code-block:: python

    >>> pid = create_zombie()
    >>> p = psutil.Process(pid)

...but every time we queried it we got a NoSuchProcess exception:

.. code-block:: python

    >>> psutil.name()
      File "psutil/__init__.py", line 374, in _init
        raise NoSuchProcess(pid, None, msg)
    psutil.NoSuchProcess: no process found with pid 123

That was misleading though because the PID technically still existed:

.. code-block:: python

    >>> psutil.pid_exists(p.pid)
    True

Furthermore, depending on what platform you were on, certain process stats could still be queried (instead of raising NoSuchProcess):

.. code-block:: python

    >>> psutil.cmdline()
    ['python']

Also process_iter() did not return zombie processes at all. This was probably the worst aspect because being able to identify them is an important use case, as they signal an issue with process: if a parent process spawns a child, terminates it (via kill()), but doesn't wait() for it it will create a zombie. Long story short, the way this changed in psutil 3.0 is that:

* we now have a new ZombieProcess exception, raised every time we're not able to query a process because it's a zombie
* it is raised instead of NoSuchProcess (which was incorrect and misleading)
* it is still backward compatible (meaning you won't have to change your old code) because it inherits from NoSuchProcess
* process_iter() finally works, meaning you can safely identify zombie processes like this:

.. code-block:: python

    import psutil
    zombies = []
    for p in psutil.process_iter():
        try:
            if p.status() == psutil.STATUS_ZOMBIE:
                zombies.append(p)
        except NoSuchProcess:
            pass

Removal of deprecated APIs
--------------------------

This is another big one, probably the biggest. In a previous blog post I already talked about deprecated APIs. What I did back then (January 2014) was to rename and officially deprecate different APIs and provide aliases for them so that people wouldn't yell at me because I broke their existent code. The most interesting deprecation was certainly the one affecting module constants and the hack which was used in order to provide "module properties". With this new release I decided to get rid of all those aliases. I'm sure this will cause problems but hey! This is a new major release, right? =). Plus the amount of crap which was removed is impressive (see the `commit <https://github.com/giampaolo/psutil/commit/ab211934af0acf99091e4cd534fc5bbe7fd3b233>`__). Here's the old aliases which are now gone for good (or bad, depending on how much headache they will cause you):

Removed module functions and constants
--------------------------------------

+------------------------------+---------------------------------+
| Already deprecated name      | New name                        |
+==============================+=================================+
| psutil.BOOT_TIME()           | psutil.boot_time()              |
+------------------------------+---------------------------------+
| psutil.NUM_CPUS()            | psutil.cpu_count()              |
+------------------------------+---------------------------------+
| psutil.TOTAL_PHYMEM()        | psutil.virtual_memory().total   |
+------------------------------+---------------------------------+
| psutil.avail_phymem()        | psutil.virtual_memory().free    |
+------------------------------+---------------------------------+
| psutil.avail_virtmem()       | psutil.swap_memory().free       |
+------------------------------+---------------------------------+
| psutil.cached_phymem()       | psutil.virtual_memory().cached  |
+------------------------------+---------------------------------+
| psutil.get_pid_list()        | psutil.pids().cached            |
+------------------------------+---------------------------------+
| psutil.get_process_list()    |                                 |
+------------------------------+---------------------------------+
| psutil.get_users()           | psutil.users()                  |
+------------------------------+---------------------------------+
| psutil.network_io_counters() | psutil.net_io_counters()        |
+------------------------------+---------------------------------+
| psutil.phymem_buffers()      | psutil.virtual_memory().buffers |
+------------------------------+---------------------------------+
| psutil.phymem_usage()        | psutil.virtual_memory()         |
+------------------------------+---------------------------------+
| psutil.total_virtmem()       | psutil.swap_memory().total      |
+------------------------------+---------------------------------+
| psutil.used_virtmem()        | psutil.swap_memory().used       |
+------------------------------+---------------------------------+
| psutil.used_phymem()         | psutil.virtual_memory().used    |
+------------------------------+---------------------------------+
| psutil.virtmem_usage()       | psutil.swap_memory()            |
+------------------------------+---------------------------------+

Process methods (assuming p = psutil.Process()):

+------------------------------+---------------------------------+
| Already deprecated name      | New name                        |
+==============================+=================================+
| p.get_children()             | p.children()                    |
+------------------------------+---------------------------------+
| p.get_connections()          | p.connections()                 |
+------------------------------+---------------------------------+
| p.get_cpu_affinity()         | p.cpu_affinity()                |
+------------------------------+---------------------------------+
| p.get_cpu_percent()          | p.cpu_percent()                 |
+------------------------------+---------------------------------+
| p.get_cpu_times()            | p.cpu_times()                   |
+------------------------------+---------------------------------+
| p.get_io_counters()          | p.io_counters()                 |
+------------------------------+---------------------------------+
| p.get_ionice()               | p.ionice()                      |
+------------------------------+---------------------------------+
| p.get_memory_info()          | p.memory_info()                 |
+------------------------------+---------------------------------+
| p.get_ext_memory_info()      | p.memory_info_ex()              |
+------------------------------+---------------------------------+
| p.get_memory_maps()          | p.memory_maps()                 |
+------------------------------+---------------------------------+
| p.get_memory_percent()       |  p.memory_percent()             |
+------------------------------+---------------------------------+
| p.get_nice()                 | p.nice()                        |
+------------------------------+---------------------------------+
| p.get_num_ctx_switches()     | p.num_ctx_switches()            |
+------------------------------+---------------------------------+
| p.get_num_fds()              | p.num_fds()                     |
+------------------------------+---------------------------------+
| p.get_num_threads()          | p.num_threads()                 |
+------------------------------+---------------------------------+
| p.get_open_files()           |  p.open_files()                 |
+------------------------------+---------------------------------+
| p.get_rlimit()               | p.rlimit()                      |
+------------------------------+---------------------------------+
| p.get_threads()              | p.threads()                     |
+------------------------------+---------------------------------+
| p.getcwd()                   | p.cwd()                         |
+------------------------------+---------------------------------+
| p.set_cpu_affinity()         | p.cpu_affinity()                |
+------------------------------+---------------------------------+
| p.set_ionice()               | p.ionice()                      |
+------------------------------+---------------------------------+
| p.set_nice()                 | p.nice()                        |
+------------------------------+---------------------------------+
| p.set_rlimit()               | p.rlimit()                      |
+------------------------------+---------------------------------+

If your code suddenly breaks with AttributeError after you upgraded psutil it means you were using one of those deprecated aliases. In that case just take a look at the table above and rename stuff in accordance.

Bug fixes
---------

I fixed a lot of stuff (full list `here <https://github.com/giampaolo/psutil/blob/master/HISTORY.rst>`__), but here's the list of things which I think are worth mentioning:

* `#512 <https://github.com/giampaolo/psutil/issues/512>`__: [FreeBSD] fix segfault in net_connections().
* `#593 <https://github.com/giampaolo/psutil/issues/593>`__: [FreeBSD] Process.memory_maps() segfaults.
* `#606 <https://github.com/giampaolo/psutil/issues/606>`__: Process.parent() may swallow NoSuchProcess exceptions.
* `#614 <https://github.com/giampaolo/psutil/issues/614>`__: [Linux]: cpu_count(logical=False) return the number of physical CPUs instead of physical cores.
* `#628 <https://github.com/giampaolo/psutil/issues/628>`__: [Linux] Process.name() truncates process name in case it contains spaces or parentheses.

Ease of development
-------------------

These are not enhancements you will directly benefit from but I put some effort into making my life easier every time I work on psutil.

* I care about psutil code being fully `PEP8 <https://www.python.org/dev/peps/pep-0008/>`__ compliant so I added a `pre-commit <https://github.com/giampaolo/psutil/blob/master/.git-pre-commit>`__ GIT hook which runs `flake8 <https://pypi.python.org/pypi/flake8>`__ on every commit and rejects it if the coding style is not compliant. The way I install this is via `make install-git-hooks <https://github.com/giampaolo/psutil/blob/82da82a6bb94ed5c6faf9d762ef4ad0fec18f01b/Makefile#L108)>`__.
* I added a ``make install-dev-deps`` command which installs all deps and stuff which is useful for testing (ipdb, coverage, etc).
* A new ``make coverage`` command which runs `coverage <http://nedbatchelder.com/code/coverage/>`__. With this I discovered some of parts in the code which weren't covered by tests and I fixed that.
* I started using `tox <https://github.com/giampaolo/psutil/blob/master/tox.ini>`__ to easily test psutil against all supported Python versions (from 2.6 to 3.4) in one shot.
* I `reorganized tests <https://github.com/giampaolo/psutil/issues/629>`__ so that now they can be easily executed with py.test and nose (before, only unittest runner was fully supported)

Final words
-----------

I must say I'm pretty satisfied with how psutil is going and the satisfaction I still get every time I work on it. Right now it gets almost `800.000 download a month <https://pypi.python.org/pypi/psutil#downloads>`__, which is pretty great for a Python library. As of right now I consider psutil almost "completed" in terms of features, meaning I'm basically running out of ideas on what I should add next (see `TODO <https://github.com/giampaolo/psutil/blob/master/TODO>`__). From now on the future development will probably focus on adding support for more exotic platforms (`OpenBSD <https://github.com/giampaolo/psutil/issues/562>`__, `NetBSD <https://github.com/giampaolo/psutil/pull/557>`__, `Android <https://github.com/giampaolo/psutil/issues/355>`__). There also have been some discussions on python-ideas mailing list about `including psutil into Python stdlib <https://mail.python.org/pipermail//python-ideas/2014-October/029835.html>`__ but, assuming that will ever happen, it's still far away in the future as it would require a lot of time which I currently don't have. That should be all. I hope you will all enjoy this new release.
