psutil 2.0
##########

:date: 2014-03-10
:tags: psutil, python

The time has finally come: `psutil <https://github.com/giampaolo/psutil/>`__ 2.0 is out! This is a release which took me a considerable amount of effort and careful thinking during the past 4 months as I went through a major **rewrite and reorganization** of both python and C extension modules. To get a sense of how much has changed you can compare the differences with the old 1.2.1 version by running "hg diff -r release-1.2.1:release-2.0.0" which will produce more than **22,000 lines** of output! In those 22k lines I tried to nail down all the quirks the project had accumulated since its start 4 years ago and the resulting code base is now cleaner than ever, more manageable and fully compliant with PEP-7 and PEP-8 guidelines.
There were some difficult decisions because many of the changes I introduced are not backward compatible so I was concerned with the pain this may cause existing users. I kind of still am, but I'm sure the transition will be well perceived in the long run as it will result in more manageable user code. OK, enough with the preface and let's see what changed.

API changes
-----------

I already wrote a detailed `blog post <psutil-20-api-redesign>`_ about what changed so I recommend you to use that as the official reference on how to port your code.

RST documentation
-----------------

I've never been happy with the old doc hosted on Google Code. The markup language provided by Google is pretty limited, plus it's not put under revision control. New doc is more detailed, it uses reStructuredText as the markup language, it lives in the same code repository as psutil's and it is hosted on the excellent readthedocs web site: http://psutil.readthedocs.org/

Physical CPUs count
-------------------

You're now able to distinguish between logical and physical CPUs:

.. code-block:: python

    >>> psutil.cpu_count()  # logical
    4
    >>> psutil.cpu_count(logical=False)  # physical cores only
    2

Full story is in issue 427 (code.google.com/p/psutil/issues/detail?id=427).

Process instances are hashable
------------------------------

Basically this means process instances can now be checked for equality and can be used with set()s:

.. code-block:: python

    >>> p1 = psutil.Process()
    >>> p2 = psutil.Process()
    >>> p1 == p2
    True
    >>> set((p1, p2))
    set([<psutil.Process(pid=8217, name='python') at 140007043550608>])

Full story is in issue 452 (code.google.com/p/psutil/issues/detail?id=452).

Speedups
--------

* #477 (code.google.com/p/psutil/issues/detail?id=477): process `cpu_percent()` is about 30% faster.
* #478 (code.google.com/p/psutil/issues/detail?id=478): (Linux) almost all APIs are about 30% faster on Python 3.X.

Other improvements and bugfixes
-------------------------------

* #424 (code.google.com/p/psutil/issues/detail?id=424): Windows installers for Python 3.X 64-bit
* #447 (code.google.com/p/psutil/issues/detail?id=447): `psutil.wait_procs()` timeout parameter is now optional.
* #459 (code.google.com/p/psutil/issues/detail?id=459): a Makefile is now available for running tests and other repetitive tasks (also on Windows)
* #463 (code.google.com/p/psutil/issues/detail?id=463): timeout parameter of ``cpu_percent*`` functions defaults to 0.0 because it was a common trap to introduce slowdowns.
* #340 (code.google.com/p/psutil/issues/detail?id=340): (Windows) process `open_files()` no longer hangs.
* #448 (code.google.com/p/psutil/issues/detail?id=448): (Windows) fixed a memory leak affecting `children()` and `ppid()` methods.
* #461 (code.google.com/p/psutil/issues/detail?id=461): namedtuples are now pickle-able.
* #474 (code.google.com/p/psutil/issues/detail?id=474): (Windows) `Process.cpu_percent()` is no longer capped at 100%

OK, that's all folks. I hope you will enjoy this new version and report your feedback.

