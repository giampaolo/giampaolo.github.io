System load average on Windows
##############################

:date: 2020-06-25
:tags: psutil, windows, windows, unittest, travel, python

New `psutil <https://github.com/giampaolo/psutil/>`__ 5.6.2 release implements an emulation of `os.getloadavg() <https://docs.python.org/3/library/os.html#os.getloadavg>`__ on Windows which was kindly `contributed by Ammar Askar <https://github.com/giampaolo/psutil/pull/1485>`__ who originally implemented it for `cPython's test suite <https://github.com/python/cpython/pull/8357/files>`__. This idea has been floating around for quite a while. The first proposal dates back to `2010 <https://code.google.com/archive/p/psutil/issues/139>`__, when psutil was still hosted on Google Code, and it popped up `multiple times <https://github.com/giampaolo/psutil/issues?utf8=%E2%9C%93&q=getloadavg>`__ throughout the years. There was/is a bunch of info on internet mentioning the bits with which it's theoretically possible to do this (the so called System Processor Queue Length), but I couldn't find any real implementation. A `Google search <https://www.google.com/search?client=ubuntu&hs=2EI&channel=fs&ei=LafCXO2ZE8PKswX9kY-wAw&q=windows+load+average&oq=windows+load+average&gs_l=psy-ab.3..0j0i22i30l7.12536.13873..14008...0.0..0.482.2591.4-6......0....1..gws-wiz.......0i71j0i131.37ys3SB25pE>`__ tells there is quite some demand for this, but very few tools out there providing this natively (the only one I could find is this `sFlowTrend <https://blog.sflow.com/2011/02/windows-load-average.html>`__ tool and `Zabbix <https://www.zabbix.com/forum/zabbix-help/50423-windows-cpu-load>`__), so I'm very happy this finally landed into psutil / Python.

Other improvements and bugfixes in psutil 5.6.2
-----------------------------------------------

The full list is `here <https://github.com/giampaolo/psutil/blob/master/HISTORY.rst#562>`__ but I would like to mention a couple:

* `1476 <https://github.com/giampaolo/psutil/issues/1476>`__: the possibility to set process' high I/O priority on Windows

* `1458 <https://github.com/giampaolo/psutil/issues/1476>`__: colorized test output. I admit nobody will use this directly but it's very cool and I'm porting it to a bunch of other projects I work on (e.g. pyftpdlib). Also, perhaps this could be a good candidate for a small module to put on PYPI which can also include some functionalities taken from pytest and which I'm gradually re-implementing in unittest module amongst which:

  - `1478 <https://github.com/giampaolo/psutil/issues/1478>`__: re-running failed tests

  - display test timings/durations: this is something I'm contributing to cPython, see `BPO-4080 <https://bugs.python.org/issue4080>`__ and and `PR-12271 <https://github.com/python/cpython/pull/12271/files>`__

About me
--------

I'm currently in China (Shenzhen) for a mix of vacation and work, and I will likely take a break from Open Source for a while (likely 2.5 months, during which I will also go to Philippines and Japan - I love Asia ;-)).

External
--------

* `Reddit <https://www.reddit.com/r/Python/comments/bhji0m/new_psutil_562_with_load_average_emulation_on/>`__

