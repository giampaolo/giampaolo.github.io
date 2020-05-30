Real process memory and environ in Python
#########################################

:date: 2016-02-17
:tags: psutil, memory

New psutil 4.0.0 is out, with some interesting news about process memory metrics. I'll just get straight to the point and describe what's new.

"Real" process memory info
--------------------------

Determining how much memory a process **really** uses is not an easy matter (see `this <https://lwn.net/Articles/230975/>`__ and `this <http://bmaurer.blogspot.it/2006/03/memory-usage-with-smaps.html>`__). RSS (Resident Set Size), which is what most people usually rely on, is misleading because it includes both the memory which is unique to the process and the memory shared with other processes. What would be more interesting in terms of profiling is the memory which would be freed if the process was terminated **right now**. In the Linux world this is called USS (Unique Set Size), and this is the major feature which was introduced in psutil 4.0.0 (not only for Linux but also for Windows and OSX).

USS memory
----------

The USS (Unique Set Size) is the memory which is unique to a process and which would be freed if the process was terminated right now. On Linux this can be determined by parsing all the "private" blocks in /proc/pid/smaps. The Firefox team pushed this further and managed to do the same also on `OSX and Windows <https://dxr.mozilla.org/mozilla-central/rev/aa90f482e16db77cdb7dea84564ea1cbd8f7f6b3/xpcom/base/nsMemoryReporterManager.cpp>`__, which is great. New version of psutil is now able to do the same:

.. code-block:: python

    >>> psutil.Process().memory_full_info()
    pfullmem(rss=101990, vms=521888, shared=38804, text=28200, lib=0, data=59672, dirty=0, uss=81623, pss=91788, swap=0)

PSS and swap
------------

On Linux there are two additional metrics which can also be determined via /proc/pid/smaps: PSS and swap. PSS, aka "Proportional Set Size", represents the amount of memory shared with other processes, accounted in a way that the amount is divided evenly between the processes that share it. I.e. if a process has 10 MBs all to itself (USS) and 10 MBs shared with another process, its PSS will be 15 MBs. "swap" is simply the amount of memory that has been swapped out to disk. With memory_full_info() it is possible to implement a tool `like this <https://github.com/giampaolo/psutil/blob/master/scripts/procsmem.py>`__, similar to `smem <https://www.selenic.com/smem/>`__ on Linux, which provides a list of processes sorted by "USS". It is interesting to notice how RSS differs from USS:

::

    ~/svn/psutil$ ./scripts/procsmem.py
    PID     User    Cmdline                            USS     PSS    Swap     RSS
    ==============================================================================
    ...
    3986    giampao /usr/bin/python3 /usr/bin/indi   15.3M   16.6M      0B   25.6M
    3906    giampao /usr/lib/ibus/ibus-ui-gtk3       17.6M   18.1M      0B   26.7M
    3991    giampao python /usr/bin/hp-systray -x    19.0M   23.3M      0B   40.7M
    3830    giampao /usr/bin/ibus-daemon --daemoni   19.0M   19.0M      0B   21.4M
    20529   giampao /opt/sublime_text/plugin_host    19.9M   20.1M      0B   22.0M
    3990    giampao nautilus -n                      20.6M   29.9M      0B   50.2M
    3898    giampao /usr/lib/unity/unity-panel-ser   27.1M   27.9M      0B   37.7M
    4176    giampao /usr/lib/evolution/evolution-c   35.7M   36.2M      0B   41.5M
    20712   giampao /usr/bin/python -B /home/giamp   45.6M   45.9M      0B   49.4M
    3880    giampao /usr/lib/x86_64-linux-gnu/hud/   51.6M   52.7M      0B   61.3M
    20513   giampao /opt/sublime_text/sublime_text   65.8M   73.0M      0B   87.9M
    3976    giampao compiz                          115.0M  117.0M      0B  130.9M
    32486   giampao skype                           145.1M  147.5M      0B  149.6M

Implementation
--------------

In order to get these values (USS, PSS and swap) we need to pass through the whole process address space. This usually requires higher user privileges and is considerably slower than getting the "usual" memory metrics via Process.memory_info(), which is probably the reason why tools like ps and top show RSS/VMS instead of USS. A big thanks goes to the Mozilla team which figured out all this stuff on Windows and OSX, and to Eric Rahm who put the PRs for psutil together (see #744, #745 and #746). For those of you who don't use Python and would like to port the code on other languages here's the interesting parts:

* `Linux <https://github.com/giampaolo/psutil/blob/42b34049cf96e845b6423db91f991849a2f87578/psutil/_pslinux.py#L1026>`__
* `OSX <https://github.com/giampaolo/psutil/blob/50fd31a4eaca3e24905b96d587fd08bcf313fc6b/psutil/_psutil_osx.c#L568>`__
* `Windows <https://github.com/giampaolo/psutil/blob/50fd31a4eaca3e24905b96d587fd08bcf313fc6b/psutil/_psutil_windows.c#L811>`__

Memory type percent
-------------------

After `reorganizing process memory APIs <https://github.com/giampaolo/psutil/pull/744#issuecomment-180054438>`_ I decided to add a new memtype parameter to Process.memory_percent(). With this it is now possible to compare a specific memory type (not only RSS) against the total physical memory. E.g.

.. code-block:: python

    >>> psutil.Process().memory_percent(memtype='pss')
    0.06877466326787016

Process environ
---------------

Second biggest improvement in psutil 4.0.0 is the ability to determine the process environment variables. This opens interesting possibilities about process recognition and monitoring techniques. For instance, one might start a process by passing a certain custom environment variable, then iterate over all processes to find the one of interest (and figure out whether it's running or whatever):

.. code-block:: python

    import psutil
    for p in psutil.process_iter():
        try:
            env = p.environ()
        except psutil.Error:
            pass
        else:
            if 'MYAPP' in env:
                ...


Process environ was a `long standing issue <https://code.google.com/archive/p/psutil/issues/52>`_ (year 2009) who I gave up to implement because the Windows implementation worked for the current process only. Frank Benkstein `solved that <https://github.com/giampaolo/psutil/pull/747>`__ and the process environ can now be determined on Linux, Windows and OSX for all processes (of course you may still bump into AccessDenied for processes owned by another user):

.. code-block:: python

    >>> import psutil
    >>> from pprint import pprint as pp
    >>> pp(psutil.Process().environ())
    {...
     'CLUTTER_IM_MODULE': 'xim',
     'COLORTERM': 'gnome-terminal',
     'COMPIZ_BIN_PATH': '/usr/bin/',
     'HOME': '/home/giampaolo',
     'PWD': '/home/giampaolo/svn/psutil',
      }
    >>>

It must be noted that the resulting dict usually does not reflect changes made after the process started (e.g. ``os.environ['MYAPP'] = '1'``). Again, for whoever is interested in doing this in other languages, here's the interesting parts:

* `Linux <https://github.com/giampaolo/psutil/blob/50fd31a4eaca3e24905b96d587fd08bcf313fc6b/psutil/_pslinux.py#L928>`_
* `OSX <https://github.com/giampaolo/psutil/blob/50fd31a4eaca3e24905b96d587fd08bcf313fc6b/psutil/arch/osx/process_info.c#L241>`_
* `Windows <https://github.com/giampaolo/psutil/pull/747>`_

Extended disk IO stats
----------------------

``psutil.disk_io_counters()`` has been extended to report additional metrics on Linux and FreeBSD:

* busy_time, which is the time spent doing actual I/Os (in milliseconds).
* read_merged_count and write_merged_count (Linux only), which is number of merged reads and writes (see `iostats <https://www.kernel.org/doc/Documentation/iostats.txt>`_ doc)

With these new metrics it is possible to have a better representation of actual `disk utilization <https://github.com/giampaolo/psutil/issues/756>`_, similarly to ``iostat`` command on Linux.

OS constants
------------

Given the increasing number of platform-specific metrics I added a new set of constants to quickly differentiate what platform you're on: ``psutil.LINUX``, ``psutil.WINDOWS``, etc. Main bug fixes:

* `#734 <https://github.com/giampaolo/psutil/issues/734>`_: on Python 3 invalid UTF-8 data was not correctly handled for proces ``name()``, ``cwd()``, ``exe()``, ``cmdline()`` and ``open_files()`` methods, resulting in UnicodeDecodeError. This was affecting all platforms. Now surrogateescape error handler is used as a workaround for replacing the corrupted data.
* `#761 <https://github.com/giampaolo/psutil/issues/761>`_: [Windows] ``psutil.boot_time()`` no longer wraps to 0 after 49 days.
* `#767 <https://github.com/giampaolo/psutil/issues/767>`_: [Linux] ``disk_io_counters()`` may raise ValueError on 2.6 kernels and it's  broken on 2.4 kernels.
* `#764 <https://github.com/giampaolo/psutil/issues/764>`_: psutil can now be compiled on NetBSD-6.X.
* `#704 <https://github.com/giampaolo/psutil/issues/704>`_: psutil can now be compiled on Solaris sparc.

Complete list of bug fixes is available `here <https://github.com/giampaolo/psutil/blob/master/HISTORY.rst>`_.

Porting code
------------

Being 4.0.0 a major version, I took the chance to (lightly) change / break some APIs.

* ``Process.memory_info()`` no longer returns just an (rss, vms) namedtuple. Instead it returns a namedtuple of variable length, changing depending on the platform (rss and vms are always present though, also on Windows). Basically it returns the same result of old ``memory_info_ex()``. This shouldn't break your existent code, unless you were doing ``rss, vms = p.memory_info()``.
* At the same time process_memory_info_ex() is now deprecated. The method is still there as an alias for ``memory_info()``, issuing a deprecation warning.
* ``psutil.disk_io_counters()`` returns 2 additional fields on Linux and 1 additional field on FreeBSD.
* ``psutil.disk_io_counters()`` on NetBSD and OpenBSD no longer return write_count and read_count metrics because the kernel do not provide them (we were returning the busy time instead). I also don't expect this to be a big issue because NetBSD and OpenBSD support is very recent.

Final notes and looking for a job
---------------------------------

OK, this is it. I would like to spend a couple more words to announce the world that I'm currently unemployed and looking for a remote gig again! =) I want remote because my plan for this year is to remain in Prague (Czech Republic) and possibly spend 2-3 months in Asia. If you know about any company who's looking for a Python backend dev who can work from afar feel free to share my `Linkedin profile <https://www.linkedin.com/in/grodola/>`_ or mail me at g.rodola [at] gmail [dot] com.

External links
--------------

* `reddit <https://www.reddit.com/r/Python/comments/469p2c/psutil_400_real_process_memory_info_and_process/>`_
* `hacker news <https://news.ycombinator.com/item?id=11119298>`_

