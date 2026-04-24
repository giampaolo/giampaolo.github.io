Announcing psutil 5.3.0
#######################

:date: 2017-09-03
:tags: psutil, travel, python

`psutil <https://github.com/giampaolo/psutil/>`__ 5.3.0 is finally out. This release is a major one, bigger than any release before it in terms of improvements and bugfixes. It is interesting to notice how huge the `diff <https://github.com/giampaolo/psutil/compare/release-5.2.2...release-5.3.0#files_bucket>`__ between 5.2.2 and 5.3.0 is. This is because I've been travelling quite a lot this year, so I kept postponing it. It may sound weird but I consider publishing a new release and writing a blog post about it more stressful than working on the release itself. =). Anyway, here goes.

Full Unicode support
--------------------

String-returning APIs (``Process.exe()``, ``Process.cwd()``, ``Process.username()``, etc.) are now Unicode-correct on both Python 2 and 3 (`#1040 <https://github.com/giampaolo/psutil/issues/1040>`__), see `detailed separate blog post </blog/2017/psutil-530-fixing-unicode.html>`__.

Improved process_iter()
-----------------------

`process_iter() <https://psutil.readthedocs.io/en/latest/#psutil.process_iter>`__ now accepts ``attrs`` and ``ad_value`` parameters, letting you pre-fetch process attributes in one shot and skip the ``try/except NoSuchProcess`` boilerplate, see `detailed separate blog post </blog/2017/psutil-530-improved-process-iter.html>`__.

Automatic overflow handling of numbers
--------------------------------------

On very busy or long-lived systems, numbers returned by `disk_io_counters() <https://psutil.readthedocs.io/en/latest/#psutil.disk_io_counters>`__ and `net_io_counters() <https://psutil.readthedocs.io/en/latest/#psutil.net_io_counters>`__ functions may wrap (restart from zero). Up to version 5.2.x you had to take this into account, while now this is automatically handled by psutil (see: `#802 <https://github.com/giampaolo/psutil/issues/802>`__). If a "counter" restarts from 0 psutil will add the value from the previous call for you so that numbers will never decrease. This is crucial for applications monitoring disk or network I/O in real time. Old behavior can be resumed by passing the `nowrap=True` argument.

SunOS Process environ()
-----------------------

`Process.environ() <https://psutil.readthedocs.io/en/latest/#psutil.Process.environ>`__ is now available also on SunOS (see `#1091 <https://github.com/giampaolo/psutil/pull/1091>`__).

Other improvements and bug fixes
--------------------------------

Amongst others, here are a couple of important bug fixes I'd like to mention:

* `#1044 <https://github.com/giampaolo/psutil/pull/1044>`__: on OSX different `Process` methods could incorrectly raise `AccessDenied` for zombie processes. This was due to the poor proc_pidpath OSX API.
* `#1094 <https://github.com/giampaolo/psutil/pull/1094>`__: on Windows, `pid_exists()` may lie due to the poor `OpenProcess` Windows API which can return a handle even when a process PID no longer exists. This had repercussions for many Process methods such as `cmdline() <https://psutil.readthedocs.io/en/latest/#psutil.Process.cmdline>`__, `environ() <https://psutil.readthedocs.io/en/latest/#psutil.Process.environ>`__, `cwd() <https://psutil.readthedocs.io/en/latest/#psutil.Process.cwd>`__, `connections() <https://psutil.readthedocs.io/en/latest/#psutil.Process.connections>`__ and others which could have unpredictable behaviors such as returning empty data or erroneously raising `NoSuchProcess` exceptions. For the same reason (broken `OpenProcess` API), processes could unexpectedly stick around after using `terminate() <https://psutil.readthedocs.io/en/latest/#psutil.Process.terminate>`__ and `wait() <https://psutil.readthedocs.io/en/latest/#psutil.Process.wait>`__.

BSD systems also received some love (NetBSD and OpenBSD in particular). Different memory leaks were fixed and functions returning connected sockets were partially rewritten. The full list of enhancements and bug fixes can be seen `here <https://psutil.readthedocs.io/latest/changelog.html>`__.

About me
--------

I would like to spend a couple more words about my current situation. Last year (2016) I relocated to Prague and remote worked from there the whole year (it's been cool - great city!). This year I have mainly been resting in Turin (Italy) due to some health issues and travelling across Asia once I started to recover. I am currently in Shenzhen, China, and unless the current situation with North Korea gets worse I'm planning to continue my trip until November and visit Taiwan, South Korea and Japan. Once I'm finished, the plan is to briefly return to Turin (Italy) and finally return to Prague. By then I will probably be looking for a new (remote) gig again, so if you have anything for me by November feel free to send me a message. ;-)
