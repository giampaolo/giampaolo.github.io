psutil 2.0 API redesign
#######################

:date: 2014-01-11
:tags: psutil, api-design, python

This my second blog post is going to be about `psutil <https://github.com/giampaolo/psutil/>`__ 2.0, a major release in which I decided to reorganize the existing API for the sake of consistency. At the time of writing psutil 2.0 is still under development and the intent of this blog post is to serve as an official reference which describes how you should port your existent code base. In doing so I will also explain why I decided to make these changes. Despite many APIs will still be available as aliases pointing to the newer ones, the overall changes are numerous and many of them are not backward compatible. I'm sure many people will be sorely bitten but I think this is for the better and it needed to be done, hopefully for the first and last time. OK, here we go now.

Module constants turned into functions
--------------------------------------

**What changed**

+----------------------+-------------------------------+
| Old name             | Replacement                   |
+======================+===============================+
| psutil.BOOT_TIME     | psutil.boot_time()            |
+----------------------+-------------------------------+
| psutil.NUM_CPUS      | psutil.cpu_count()            |
+----------------------+-------------------------------+
| psutil.TOTAL_PHYMEM  | psutil.virtual_memory().total |
+----------------------+-------------------------------+

**Why I did it**

I already talked about this more extensively in this `blog post <../../2013/making-constants-part-of-your-api-is-evil/>`_. In short: other than introducing unnecessary slowdowns, calculating a module level constant at import time is dangerous because in case of error the whole app will crash. Also, the represented values may be subject to change (think about the system clock) but the constant cannot be updated.
Thanks to this hack accessing the old constants still works and produces a DeprecationWarning.

Module functions renamings
--------------------------

**What changed**

+------------------------+-------------------------------+
| Old name               | Replacement                   |
+========================+===============================+
| psutil.get_boot_time() | psutil.boot_time()            |
+------------------------+-------------------------------+
| psutil.get_pid_list()  | psutil.pids()                 |
+------------------------+-------------------------------+
| psutil.get_users()     | psutil.users()                |
+------------------------+-------------------------------+

**Why I did it**

They were the only module level functions having a ``get_`` prefix. All others do not.

Process class' methods renamings
--------------------------------

All methods lost their ``get_`` and ``set_`` prefixes. A single method can now be used for both getting and setting (if a value is passed). Assuming p = psutil.Process():

+--------------------------+-------------------------------+
| Old name                 | Replacement                   |
+==========================+===============================+
| p.get_children()         | p.children()                  |
+--------------------------+-------------------------------+
| p.get_connections()      | p.connections()               |
+--------------------------+-------------------------------+
| p.get_cpu_affinity()     | p.cpu_affinity()              |
+--------------------------+-------------------------------+
| p.get_cpu_percent()      | p.cpu_percent()               |
+--------------------------+-------------------------------+
| p.get_cpu_times()        | p.cpu_times()                 |
+--------------------------+-------------------------------+
| p.get_io_counters()      | p.io_counters()               |
+--------------------------+-------------------------------+
| p.get_ionice()           | p.ionice()                    |
+--------------------------+-------------------------------+
| p.get_memory_info()      | p.memory_info()               |
+--------------------------+-------------------------------+
| p.get_ext_memory_info()  | p.memory_info_ex()            |
+--------------------------+-------------------------------+
| p.get_memory_maps()      | p.memory_maps()               |
+--------------------------+-------------------------------+
| p.get_memory_percent()   | p.memory_percent()            |
+--------------------------+-------------------------------+
| p.get_nice()             | p.nice()                      |
+--------------------------+-------------------------------+
| p.get_num_ctx_switches() | p.num_ctx_switches()          |
+--------------------------+-------------------------------+
| p.get_num_fds()          | p.num_fds()                   |
+--------------------------+-------------------------------+
| p.get_num_threads()      | p.num_threads()               |
+--------------------------+-------------------------------+
| p.get_open_files()       | p.open_files()                |
+--------------------------+-------------------------------+
| p.get_rlimit()           | p.rlimit()                    |
+--------------------------+-------------------------------+
| p.get_threads()          | p.threads()                   |
+--------------------------+-------------------------------+
| p.getcwd()               | p.cwd()                       |
+--------------------------+-------------------------------+

...as for set_* methods:

+--------------------------+---------------------------------+
| Old name                 | Replacement                     |
+==========================+=================================+
| p.set_cpu_affinity()     | p.cpu_affinity(cpus)            |
+--------------------------+---------------------------------+
| p.set_ionice()           | p.ionice(ioclass, value=None)   |
+--------------------------+---------------------------------+
| p.set_nice()             | p.nice(value)                   |
+--------------------------+---------------------------------+
| p.set_rlimit()           | p.rlimit(resource, limits=None) |
+--------------------------+---------------------------------+

**Why I did it**

I wanted to be consistent with system-wide module level functions which have no ``get_`` prefix. After I got rid of ``get_`` prefixes removing also ``set_`` seemed natural and helped diminish the number of methods.

Process properties are now methods
----------------------------------

**What changed**

Assuming p = psutil.Process():

+--------------------------+---------------------------------+
| Old name                 | Replacement                     |
+==========================+=================================+
| p.cmdline                | p.cmdline()                     |
+--------------------------+---------------------------------+
| p.create_time            | p.create_time()                 |
+--------------------------+---------------------------------+
| p.exe                    | p.exe()                         |
+--------------------------+---------------------------------+
| p.gids                   | p.gids()                        |
+--------------------------+---------------------------------+
| p.name                   | p.name()                        |
+--------------------------+---------------------------------+
| p.parent                 | p.parent()                      |
+--------------------------+---------------------------------+
| p.ppid                   | p.ppid()                        |
+--------------------------+---------------------------------+
| p.status                 | p.status()                      |
+--------------------------+---------------------------------+
| p.uids                   | p.uids()                        |
+--------------------------+---------------------------------+
| p.username               | p.username()                    |
+--------------------------+---------------------------------+

**Why I did it**

Different reasons:

* Having a mixed API which uses both properties and methods for no particular reason is confusing and messy as you don't know whether to use "()" or not (see `here <https://code.google.com/p/psutil/source/browse/test/test_psutil.py?name=release-0.7.0#1716>`__).
* It is usually expected from a property to not perform many computations internally whereas psutil actually invokes a function every time it is accessed. This has two drawbacks:
  * you may get an exception just by accessing the property (e.g. "p.name" may raise NoSuchProcess or AccessDenied)
  * you may erroneously think properties are cached but this is true only for name, exe, and create_time.

CPU percent intervals
---------------------

**What changed**

The timeout parameter of `cpu_percent*` functions now defaults to 0.0 instead of 0.1. The functions affected are:

* psutil.Process.cpu_percent()
* psutil.cpu_percent()
* psutil.cpu_times_percent()

**Why I did it**

I originally set 0.1 as the default timeout because in order to get a meaningful percent value you need to wait some time.
Having an API which "sleeps" by default is risky though, because it's easy to forget it does so. That is particularly problematic when calling cpu_percent() for all processes: it's very easy to forget about specifying timeout=0 resulting in dramatic slowdowns which are hard to spot. For example, this code snippet might take different seconds to complete depending on the number of active processes:

.. code-block:: python

    >>> # this will be slow
    >>> for p in psutil.process_iter():
    ...    print(p.cpu_percent())

Migration strategy
------------------

Except for Process properties (name, exe, cmdline, etc.) all the old APIs are still available as aliases pointing to the newer names and raising DeprecationWarning. psutil will be very clear on what you should use instead of the deprecated API as long you start the interpreter with the "-Wd" option. This will enable deprecation warnings which were `silenced in Python 2.7 <http://bugs.python.org/issue7319>`__ (IMHO, from a developer standpoint this was a bad decision).

::

    giampaolo@ubuntu:/tmp$ python -Wd
    Python 2.7.3 (default, Sep 26 2013, 20:03:06)
    [GCC 4.6.3] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import psutil
    >>> psutil.get_pid_list()
    __main__:1: DeprecationWarning: psutil.get_pid_list is deprecated; use psutil.pids() instead
    [1, 2, 3, 6, 7, 13, ...]
    >>>
    >>>
    >>> p = psutil.Process()
    >>> p.get_cpu_times()
    __main__:1: DeprecationWarning: get_cpu_times() is deprecated; use cpu_times() instead
    pcputimes(user=0.08, system=0.03)
    >>>

If you have a solid test suite you can run tests and fix the warnings one by one.
As for the the Process properties which were turned into methods it's more difficult because whereas psutil 1.2.1 returns the actual value, psutil 2.0.0 will return the bound method:

.. code-block:: python

    # psutil 1.2.1
    >>> psutil.Process().name
    'python'
    >>>

    # psutil 2.0.0
    >>> psutil.Process().name
    <bound method Process.name of psutil.Process(pid=19816, name='python') at 139845631328144>
    >>>

What I would recommend if you want to drop support with 1.2.1 is to grep for ".name", ".exe" etc. and just replace them with ".exe()" and ".name()" one by one.
If on the other hand you want to write a code which works with both versions I see two possibilities:

* #1 check version info, like this:

.. code-block:: python

    >>> PSUTIL2 = psutil.version_info >= (2, 0)
    >>> p = psutil.Process()
    >>> name = p.name() if PSUTIL2 else p.name
    >>> exe = p.exe() if PSUTIL2 else p.exe

* #2 get rid of all ".name", ".exe" occurrences you have in your code and use as_dict() instead:

.. code-block:: python

    >>> p = psutil.Process()
    >>> pinfo = p.as_dict(attrs=["name", "exe"])
    >>> pinfo
    {'exe': '/usr/bin/python2.7', 'name': 'python'}
    >>> name = pinfo['name']
    >>> exe = pinfo['exe']

New features introduced in 2.0.0
--------------------------------

Ok, enough with the bad news. =) psutil 2.0.0 is not only about code breakage. I also had the chance to integrate a bunch of interesting features.

* `#427 <https://code.google.com/p/psutil/issues/detail?id=427>`__: you're now able to distinguish between the number of logical and physical CPUs:

.. code-block:: python

    >>> psutil.cpu_count()  # logical
    4
    >>> psutil.cpu_count(logical=False)  # physical cores only
    2

* `#452 <https://code.google.com/p/psutil/issues/detail?id=452>`__: process classes are now hashable and can be checked for equality. That means you can use Process objects with sets (finally!).
* `#447 <https://code.google.com/p/psutil/issues/detail?id=447>`__: psutil.wait_procs() "timeout" parameter is now optional
* `#461 <https://code.google.com/p/psutil/issues/detail?id=461>`__: functions returning namedtuples are now pickle-able
* `#459 <https://code.google.com/p/psutil/issues/detail?id=459>`__: a Makefile is now available to automatize repetitive tasks such as build, install, running tests etc. There's also a make.bat for Windows.
* introduced unittest2 module as a requirement for running tests

