psutil 2.1.2 and Python wheels
##############################

:date: 2014-09-21
:tags: psutil, wheels, travel, python

`psutil <https://github.com/giampaolo/psutil/>`__ 2.1.2 is out. This release has been cooking for a while now, and that's because I've been travelling for the past 3 months between Spain, Japan and Germany. Hopefully I will be staying in Berlin for a while now, so I will have more time to dedicate to the project. The main new "feature" of this release is that other than the exe files, Windows users can now also benefit of `Python wheels <http://pythonwheels.com/>`__ (full story is `here <https://github.com/giampaolo/psutil/issues/505>`__) which are available on PYPI. Frankly I don't know much about the new wheels packaging system but long story short is that Windows users can now install psutil via pip and therefore also include it as a dependency into requirements.txt. Other than this 2.1.2 can basically be considered a bug-fix release, including some important fixes amongst which:

* `#506 <https://github.com/giampaolo/psutil/issues/506>`__: restored Python 2.4 compatibility
* `#340 <https://github.com/giampaolo/psutil/issues/340>`__: Process.get_open_files() no longer hangs on Windows (this was a very old and high-priority issue)
* `#501 <https://github.com/giampaolo/psutil/issues/501>`__: disk_io_counters() may return negative values on Windows
* `#504 <https://github.com/giampaolo/psutil/issues/504>`__: (Linux) couldn't build RPM packages via setup.py

The list of all fixes can be found `here <https://github.com/giampaolo/psutil/blob/master/HISTORY.rst>`__. For the next release I plan to drop support for Python 2.4 and 2.5 and hopefully network interfaces information similarly to `ifconfig <https://github.com/giampaolo/psutil/issues/376>`__.
