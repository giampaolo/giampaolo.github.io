System load average on Windows in Python
########################################

:date: 2019-05-29
:tags: psutil, windows, python, unittest, travel
:slug: system-load-average-on-windows-in-python

psutil 5.6.2 is out. It implements an emulation of `os.getloadavg() <https://docs.python.org/3/library/os.html#os.getloadavg>`__ on Windows, kindly contributed by `Ammar Askar <https://github.com/giampaolo/psutil/pull/1485>`__, who originally implemented it for `CPython's test suite <https://github.com/python/cpython/pull/8357/files>`__.

This idea has been floating around for quite a while. The first proposal dates back to `2010 <https://github.com/giampaolo/psutil/issues/139>`__, when psutil was still hosted on Google Code, and it popped up `multiple times <https://github.com/giampaolo/psutil/issues?utf8=%E2%9C%93&q=getloadavg>`__ over the years. There's a bunch of info online mentioning the pieces you'd theoretically use (the so-called ``System Processor Queue Length``), but I couldn't find any real implementation. A quick search suggests there's real demand for this, but very few tools provide it natively (the only ones I could find are `sFlowTrend <https://blog.sflow.com/2011/02/windows-load-average.html>`__ and `Zabbix <https://www.zabbix.com/forum/zabbix-help/50423-windows-cpu-load>`__). So I'm glad this finally landed in psutil / Python.

Other improvements and bugfixes in psutil 5.6.2
-----------------------------------------------

The full list is in the `changelog <https://psutil.readthedocs.io/latest/changelog.html>`__. A couple worth mentioning:

* `#1476 <https://github.com/giampaolo/psutil/issues/1476>`__: ability to set a process's high I/O priority on Windows.

* `#1458 <https://github.com/giampaolo/psutil/issues/1458>`__: colorized test output. Nobody will use this directly, but it's nice and I'm porting it to other projects I maintain (e.g. pyftpdlib). Good candidate for a small PyPI module that could also include the unittest extensions I've been re-implementing piece by piece:

  - `#1478 <https://github.com/giampaolo/psutil/issues/1478>`__: re-running failed tests.

  - display test timings / durations. This is something I'm also contributing to CPython: `BPO-4080 <https://bugs.python.org/issue4080>`__ and `PR-12271 <https://github.com/python/cpython/pull/12271/files>`__.

About me
--------

I'm currently in China (Shenzhen) for a mix of vacation and work, and I will likely take a break from Open Source for a while (about 2.5 months), during which I'll also go to the Philippines and Japan.

External
--------

* `Reddit <https://www.reddit.com/r/Python/comments/bhji0m/new_psutil_562_with_load_average_emulation_on/>`__
