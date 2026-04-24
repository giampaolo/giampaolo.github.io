Real process memory and environ in Python
#########################################

:date: 2016-02-17
:tags: psutil, memory, python
:slug: real-process-memory-and-environ-in-python

psutil 4.0.0 is out, with some interesting news about process memory metrics. I'll get straight to the point and describe what's new.

"Real" process memory info
--------------------------

Determining how much memory a process **really** uses is not an easy matter (see `this <https://lwn.net/Articles/230975/>`__ and `this <http://bmaurer.blogspot.it/2006/03/memory-usage-with-smaps.html>`__). RSS (Resident Set Size), which most people rely on, is misleading because it includes both memory unique to the process and memory shared with others. What's more interesting for profiling is the memory that would be freed if the process were terminated **right now**. In the Linux world this is called USS (Unique Set Size), the major feature introduced in psutil 4.0.0 (not only for Linux but also for Windows and macOS).

USS memory
----------

The USS (Unique Set Size) is the memory unique to a process, that would be freed if the process were terminated right now. On Linux it can be determined by parsing the "private" blocks in ``/proc/PID/smaps``. The Firefox team pushed this further and got it working on `macOS and Windows <https://dxr.mozilla.org/mozilla-central/rev/aa90f482e16db77cdb7dea84564ea1cbd8f7f6b3/xpcom/base/nsMemoryReporterManager.cpp>`__ too.

.. code-block:: pycon

    >>> psutil.Process().memory_full_info()
    pfullmem(rss=101990, vms=521888, shared=38804, text=28200, lib=0, data=59672, dirty=0, uss=81623, pss=91788, swap=0)

PSS and swap
------------

On Linux there are two additional metrics that can also be determined via ``/proc/PID/smaps``: PSS and swap.

``pss``, aka "Proportional Set Size", represents the amount of memory shared with other processes, accounted so that the amount is divided evenly between the processes that share it. I.e. if a process has 10 MBs all to itself (USS) and 10 MBs shared with another process, its PSS will be 15 MBs.

``swap`` is simply the amount of memory that has been swapped out to disk. With ``Process.memory_full_info()`` it is possible to implement a tool like `procsmem.py <https://github.com/giampaolo/psutil/blob/release-4.0.0/scripts/procsmem.py>`__, similar to `smem <https://www.selenic.com/smem/>`__ on Linux, which provides a list of processes sorted by ``uss``. It's interesting to see how ``rss`` differs from ``uss``:

.. code-block:: none

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

To get these values (``uss``, ``pss`` and ``swap``) we need to walk the whole process address space. This usually requires higher privileges and is considerably slower than ``Process.memory_info()``, which is probably why tools like ``ps`` and ``top`` show RSS/VMS instead of USS. A big thanks goes to the Mozilla team for figuring this out on Windows and macOS, and to `Eric Rahm <https://github.com/EricRahm>`_ who put the psutil PRs together (see `PR-744 <https://github.com/giampaolo/psutil/pull/744>`__, `PR-745 <https://github.com/giampaolo/psutil/pull/745>`__ and `PR-746 <https://github.com/giampaolo/psutil/pull/746>`__). If you don't use Python and want to port the code to another language, here are the interesting parts:

* `Linux <https://github.com/giampaolo/psutil/blob/42b34049cf96e845b6423db91f991849a2f87578/psutil/_pslinux.py#L1026>`__
* `macOS <https://github.com/giampaolo/psutil/blob/50fd31a4eaca3e24905b96d587fd08bcf313fc6b/psutil/_psutil_osx.c#L568>`__
* `Windows <https://github.com/giampaolo/psutil/blob/50fd31a4eaca3e24905b96d587fd08bcf313fc6b/psutil/_psutil_windows.c#L811>`__

Memory type percent
-------------------

After reorganizing the process memory APIs (`PR-744 <https://github.com/giampaolo/psutil/pull/744>`__), I added a new ``memtype`` parameter to ``Process.memory_percent()``. You can now compare a specific memory type (not only RSS) against the total physical memory. E.g.

.. code-block:: pycon

    >>> psutil.Process().memory_percent(memtype='pss')
    0.06877466326787016

Process environ
---------------

The second biggest improvement in psutil 4.0.0 is the ability to read a process's environment variables. This opens up interesting possibilities for process recognition and monitoring. For instance, you can start a process with a custom environment variable, then iterate over all processes to find the one of interest:

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

Process environ was a long-standing issue (`#52 <https://github.com/giampaolo/psutil/issues/52>`__, from 2009) that I gave up on because the Windows implementation only worked for the current process. `Frank Benkstein <https://github.com/fbenkstein>`_ solved that (`PR-747 <https://github.com/giampaolo/psutil/pull/747>`__), and it now works on Linux, Windows and macOS for all processes (you may still hit ``AccessDenied`` for processes owned by another user):

.. code-block:: pycon

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

Note that the resulting dict usually doesn't reflect changes made after the process started (e.g. ``os.environ['MYAPP'] = '1'``). Again, for anyone porting this to other languages, here are the interesting parts:

* `Linux <https://github.com/giampaolo/psutil/blob/50fd31a4eaca3e24905b96d587fd08bcf313fc6b/psutil/_pslinux.py#L928>`_
* `macOS <https://github.com/giampaolo/psutil/blob/50fd31a4eaca3e24905b96d587fd08bcf313fc6b/psutil/arch/osx/process_info.c#L241>`_
* `Windows <https://github.com/giampaolo/psutil/pull/747>`_

Extended disk IO stats
----------------------

``psutil.disk_io_counters()`` now reports additional metrics on Linux and FreeBSD:

* ``busy_time``: the time spent doing actual I/Os (in milliseconds).
* ``read_merged_count`` and ``write_merged_count`` (Linux only): the number of merged reads and writes (see the `iostats <https://www.kernel.org/doc/Documentation/iostats.txt>`_ doc).

These give a better picture of actual disk utilization (`#756 <https://github.com/giampaolo/psutil/issues/756>`__), similar to the ``iostat`` command on Linux.

OS constants
------------

Given the growing number of platform-specific metrics, I added a set of constants to tell which platform you're on: ``psutil.LINUX``, ``psutil.WINDOWS``, etc.

Other fixes
-----------

The complete list of changes is available in the `changelog <https://psutil.readthedocs.io/en/latest/#id22>`__.

Porting code
------------

Since 4.0.0 is a major version, I took the chance to (lightly) change / break some APIs.

* ``Process.memory_info()`` no longer returns just an (``rss``, ``vms``) namedtuple. It returns a variable-length namedtuple that varies by platform (``rss`` and ``vms`` are always present, even on Windows). Essentially the same result as the old ``Process.memory_info_ex()``. This shouldn't break your code unless you were doing ``rss, vms = p.memory_info()``.
* ``Process.memory_info_ex()`` is deprecated. It still works as an alias for ``Process.memory_info()``, issuing a ``DeprecationWarning``.
* ``psutil.disk_io_counters()`` on NetBSD and OpenBSD no longer returns ``write_count`` and ``read_count`` because the kernel doesn't provide them (we were returning the busy time instead). Should be a small issue given NetBSD and OpenBSD support is very recent.

Discussion
----------

* `Reddit <https://www.reddit.com/r/Python/comments/469p2c/psutil_400_real_process_memory_info_and_process/>`_
* `Hacker News <https://news.ycombinator.com/item?id=11119298>`_
