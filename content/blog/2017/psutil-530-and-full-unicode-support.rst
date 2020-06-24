psutil 5.3.0 and full unicode support
#####################################

:date: 2017-09-03
:tags: psutil, travel, python

`psutil <https://github.com/giampaolo/psutil/>`__ 5.3.0 is finally out. This release is a major one, as it includes tons of improvements and bugfixes, probably like no other previous release. It is interesting to notice how huge the `diff <https://github.com/giampaolo/psutil/compare/release-5.2.2...release-5.3.0#files_bucket>`__ between 5.2.2 and 5.3.0 is. This is due to the fact that I've been travelling quite a lot this year, so I kept postponing it. It may sound weird but I consider publishing a new release and write a blog post about more stressful than working on the release itself. =). Anyway, here goes.
Full Unicode support
This is the biggest change. In order to achieve this I had to refactor all functions and internals either returning or accepting a string. Incidentally this helped me having a better understanding of how Unicode works and how it should be handled at the C level in terms of differences between Python 2 and 3. Issue `#1040 <https://github.com/giampaolo/psutil/issues/1040>`__ includes all the reasonings I've been through and potentially serves as a documentation for people who are facing a similar task (handling Unicode in C for both Python 2 and 3). Up until version 5.2.x psutil functions returning a string had different problems as they could:

* raise decoding error on Python 3 in case of non-ASCII string
* return unicode instead of str (Python 2)
* return incorrect / invalid encoded data in case of non-ASCII string

5.3.0 fixes these three issues and consolidates the correct handling of Unicode strings. On Windows this was achieved by using Unicode-specific Windows APIs. The notes below describe how Unicode and strings in general are handled internally by psutil and they apply to any API returning a string such as `Process.exe <https://psutil.readthedocs.io/en/latest/#psutil.Process.exe>`__ or `Process.cwd <https://psutil.readthedocs.io/en/latest/#psutil.Process.cwd>`__, including non-filesystem related methods such as `Process.username <https://psutil.readthedocs.io/en/latest/#psutil.Process.username>`__ or `WindowsService.description <https://psutil.readthedocs.io/en/latest/#psutil.WindowsService.description>`__:

* all strings are encoded by using the OS filesystem encoding (`sys.getfilesystemencoding() <https://docs.python.org/3/library/sys.html#sys.getfilesystemencoding>`__) which varies depending on the platform (e.g. "UTF-8" on OSX, "mbcs" on Win)
* no API call is supposed to crash with UnicodeDecodeError
* instead, in case of badly encoded data returned by the OS, the following error handlers are used to replace the corrupted characters in the string:

  - Python 3: `sys.getfilesystemencodeerrors() <https://docs.python.org/3/library/sys.html#sys.getfilesystemencodeerrors>`__ (PY 3.6+) or ``"surrogatescape"`` on POSIX and "replace" on Windows

  - Python 2: "replace"

* on Python 2 all APIs return bytes (str type), never unicode
* on Python 2 you can go back to unicode by doing:

.. code-block:: python

    >>> unicode(proc.exe(), sys.getdefaultencoding(), errors="replace")

Improved process_iter() function
--------------------------------

`process_iter() <https://psutil.readthedocs.io/en/latest/#psutil.process_iter>`__ accepts two new parameters in order to invoke `Process.as_dict() <https://psutil.readthedocs.io/en/latest/#psutil.Process.as_dict>`__ internally: "attrs" and "ad_value". With this you can iterate over all processes in one shot without having to catch NoSuchProcess explicitly. Before:

.. code-block:: python

    >>> import psutil
    >>> for proc in psutil.process_iter():
    ...     try:
    ...         pinfo = proc.as_dict(attrs=['pid', 'name'])
    ...     except psutil.NoSuchProcess:
    ...         pass
    ...     else:
    ...         print(pinfo)
    ...
    {'pid': 1, 'name': 'systemd'}
    {'pid': 2, 'name': 'kthreadd'}
    {'pid': 3, 'name': 'ksoftirqd/0'}
    ...

Now:

.. code-block:: python

    >>> import psutil
    >>> for proc in psutil.process_iter(attrs=['pid', 'name']):
    ...     print(proc.info)
    ...
    {'pid': 1, 'name': 'systemd'}
    {'pid': 2, 'name': 'kthreadd'}
    {'pid': 3, 'name': 'ksoftirqd/0'}

This improves expressiveness as it makes it possible to use nice list/dict comprehensions. Here's some examples.

Processes having "python" in their name:

.. code-block:: python

    >>> from pprint import pprint as pp
    >>> pp([p.info for p in psutil.process_iter(attrs=['pid', 'name']) if 'python' in p.info['name']])
    [{'name': 'python3', 'pid': 21947},
    {'name': 'python', 'pid': 23835}]

Processes owned by user:

.. code-block:: python

    >>> import getpass
    >>> pp([(p.pid, p.info['name']) for p in psutil.process_iter(attrs=['name', 'username']) if p.info['username'] == getpass.getuser()])
    (16832, 'bash'),
    (19772, 'ssh'),
    (20492, 'python')]

Processes actively running:

.. code-block:: python

    >>> pp([(p.pid, p.info) for p in psutil.process_iter(attrs=['name', 'status']) if p.info['status'] == psutil.STATUS_RUNNING])
    [(1150, {'name': 'Xorg', 'status': 'running'}),
    (1776, {'name': 'unity-panel-service', 'status': 'running'}),
    (20492, {'name': 'python', 'status': 'running'})]

Automatic overflow handling of numbers
--------------------------------------

On very busy or long-lived system systems numbers returned by `disk_io_counters() <https://psutil.readthedocs.io/en/latest/#psutil.disk_io_counters>`__ and `net_io_counters() <https://psutil.readthedocs.io/en/latest/#psutil.net_io_counters>`__ functions may wrap (restart from zero). Up to version 5.2.x you had to take this into account while now this is automatically handled by psutil (see: `#802 <https://github.com/giampaolo/psutil/issues/802>`__). If a "counter" restarts from 0 psutil will add the value from the previous call for you so that numbers will never decrease. This is crucial for applications monitoring disk or network I/O in real time. Old behavior can be resumed by passing nowrap=True argument.

SunOS Process environ()
-----------------------

`Process.environ() <https://psutil.readthedocs.io/en/latest/#psutil.Process.environ>`__ is now available also on SunOS (see `#1091 <https://github.com/giampaolo/psutil/pull/1091>`__).

Other improvements and bug fixes
--------------------------------

Amongst others, here's a couple of important bug fixes I'd like to mention:

* `#1044 <https://github.com/giampaolo/psutil/pull/1044>`__: on OSX different Process methods could incorrectly raise AccessDenied for zombie processes. This was due to poor proc_pidpath OSX API.
* `#1094 <https://github.com/giampaolo/psutil/pull/1094>`__: on Windows, pid_exists() may lie due to the poor OpenProcess Windows API which can return a handle even when a process PID no longer exists. This had repercussions for many Process methods such as `cmdline() <https://psutil.readthedocs.io/en/latest/#psutil.Process.cmdline>`__, `environ() <https://psutil.readthedocs.io/en/latest/#psutil.Process.environ>`__, `cwd() <https://psutil.readthedocs.io/en/latest/#psutil.Process.cwd>`__, `connections() <https://psutil.readthedocs.io/en/latest/#psutil.Process.connections>`__ and others which could have unpredictable behaviors such as returning empty data or erroneously raise NoSuchProcess exceptions. For the same reason (broken OpenProcess API), processes could unexpectedly stick around after using `terminate() <https://psutil.readthedocs.io/en/latest/#psutil.Process.terminate>`__ and `wait() <https://psutil.readthedocs.io/en/latest/#psutil.Process.wait>`__.

BSD systems also received some love (NetBSD and OpenBSD in particular). Different memory leaks were fixed and functions returning connected sockets were partially rewritten. The full list of enhancement and bug fixes can be seen `here <https://github.com/giampaolo/psutil/blob/master/HISTORY.rst#530>`__.

About me
--------

I would like to spend a couple more words about my current situation. Last year (2016) I relocated to Prague and remote worked from there the whole year (it's been cool - great city!). This year I have mainly been resting in Turin (Italy) due to some health issues and travelling across Asia once I started to recover. I am currently in Shenzhen, China, and unless the current situation with North Korea gets worse I'm planning to continue my trip until November and visit Taiwan, South Korea and Japan. Once I'm finished the plan is to briefly return to Turin (Italy) and finally return to Prague. By then I will probably be looking for a new (remote) gig again, so if you have anything for me by November feel free to send me a message. ;-)
