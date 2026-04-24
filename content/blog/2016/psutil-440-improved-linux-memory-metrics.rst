Improved Linux memory metrics
#############################

:date: 2016-10-23
:tags: psutil, python, memory, linux, release
:slug: psutil-440-improved-linux-memory-metrics

OK, another psutil release. The headline of 4.4.0 is more accurate memory metrics on Linux, plus a pile of macOS fixes I'd been sitting on for years.

Linux virtual memory
--------------------

People had been complaining for a while that ``virtual_memory()`` didn't match what ``free`` reported on Linux (`#862 <https://github.com/giampaolo/psutil/issues/862>`__, `#685 <https://github.com/giampaolo/psutil/issues/685>`__, `#538 <https://github.com/giampaolo/psutil/issues/538>`__). I finally dug into it (`#887 <https://github.com/giampaolo/psutil/issues/887>`__, `PR-890 <https://github.com/giampaolo/psutil/pull/890>`__) and, funny enough, it turns out ``free`` itself was doing it wrong until `about two years ago <https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=34e431b0ae398fc54ea69ff85ec700722c9da773>`__, when somebody got tired of everyone guessing and moved the calculation into the kernel.

Starting with Linux 3.14, ``/proc/meminfo`` has a ``MemAvailable`` column. That's what psutil now uses, and the ``available`` / ``used`` fields match ``free`` exactly. On older kernels (< 3.14) psutil falls back to the `same formula <https://github.com/giampaolo/psutil/blob/a5beb29488fe75c858d30a00044cbd29d3ed3d8b/psutil/_pslinux.py#L291>`__ that kernel commit introduced.

``free``'s source code also inspired a fix that prevents available memory from overflowing total memory on `LXC containers <https://github.com/giampaolo/psutil/blob/a5beb29488fe75c858d30a00044cbd29d3ed3d8b/psutil/_pslinux.py#L435>`__.

macOS fixes
-----------

For years I did psutil's macOS development on an old 10.5 install emulated via VirtualBox, running iDeneb (a hacked macOS). I finally got access to a more recent version (El Capitan) via VirtualBox + Vagrant, and could address a pile of long-standing bugs:

* `#514 <https://github.com/giampaolo/psutil/issues/514>`__: ``Process.memory_maps()`` segfault (critical).
* `#783 <https://github.com/giampaolo/psutil/issues/783>`__: ``Process.status()`` could return ``"running"`` for zombie processes.
* `#908 <https://github.com/giampaolo/psutil/issues/908>`__: several methods could mask the real error for high-privileged PIDs, raising ``NoSuchProcess`` / ``AccessDenied`` instead of ``OSError`` / ``RuntimeError``.
* `#909 <https://github.com/giampaolo/psutil/issues/909>`__: ``Process.open_files()`` and ``Process.connections()`` could raise ``OSError`` with no exception set when the process was gone.
* `#916 <https://github.com/giampaolo/psutil/issues/916>`__: fixed many compilation warnings.

NIC netmask on Windows
----------------------

Small but nice: ``net_if_addrs()`` on Windows now returns the netmask too.

Improved procinfo.py
--------------------

`scripts/procinfo.py <https://github.com/giampaolo/psutil/blob/release-4.4.0/scripts/procinfo.py>`__ is my kitchen-sink demo script. I taught it a bunch of new tricks, so it now dumps pretty much everything psutil knows about a process:

.. code-block:: none

    $ python scripts/procinfo.py
    pid           4600
    name          chrome
    parent        4554 (bash)
    exe           /opt/google/chrome/chrome
    cwd           /home/giampaolo
    cmdline       /opt/google/chrome/chrome
    started       2016-09-19 11:12
    cpu-tspent    27:27.68
    cpu-times     user=8914.32, system=3530.59,
                  children_user=1.46, children_system=1.31
    cpu-affinity  [0, 1, 2, 3, 4, 5, 6, 7]
    memory        rss=520.5M, vms=1.9G, shared=132.6M, text=95.0M, lib=0B,
                  data=816.5M, dirty=0B
    memory %      3.26
    user          giampaolo
    uids          real=1000, effective=1000, saved=1000
    terminal      /dev/pts/2
    status        sleeping
    nice          0
    ionice        class=IOPriority.IOPRIO_CLASS_NONE, value=0
    num-threads   47
    num-fds       379
    I/O           read_count=96.6M, write_count=80.7M,
                  read_bytes=293.2M, write_bytes=24.5G
    ctx-switches  voluntary=30426463, involuntary=460108
    children      PID    NAME
                  4605   cat
                  4606   cat
                  4609   chrome
                  4669   chrome
    open-files    PATH
                  /opt/google/chrome/icudtl.dat
                  /opt/google/chrome/snapshot_blob.bin
                  /opt/google/chrome/natives_blob.bin
                  /opt/google/chrome/chrome_100_percent.pak
                  [...]
    connections   PROTO LOCAL ADDR            REMOTE ADDR               STATUS
                  UDP   10.0.0.3:3693         *:*                       NONE
                  TCP   10.0.0.3:55102        172.217.22.14:443         ESTABLISHED
                  UDP   10.0.0.3:35172        *:*                       NONE
                  TCP   10.0.0.3:32922        172.217.16.163:443        ESTABLISHED
                  UDP   :::5353               *:*                       NONE
                  UDP   10.0.0.3:59925        *:*                       NONE
    threads       TID              USER          SYSTEM
                  11795             0.7            1.35
                  11796            0.68            1.37
                  15887            0.74            0.03
                  19055            0.77            0.01
                  [...]
                  total=47
    res-limits    RLIMIT                     SOFT       HARD
                  virtualmem             infinity   infinity
                  coredumpsize                  0   infinity
                  cputime                infinity   infinity
                  datasize               infinity   infinity
                  filesize               infinity   infinity
                  locks                  infinity   infinity
                  memlock                   65536      65536
                  msgqueue                 819200     819200
                  nice                          0          0
                  openfiles                  8192      65536
                  maxprocesses              63304      63304
                  rss                    infinity   infinity
                  realtimeprio                  0          0
                  rtimesched             infinity   infinity
                  sigspending               63304      63304
                  stack                   8388608   infinity
    mem-maps      RSS      PATH
                  381.4M   [anon]
                  62.8M    /opt/google/chrome/chrome
                  15.8M    /home/giampaolo/.config/google-chrome/Default/History
                  6.6M     /home/giampaolo/.config/google-chrome/Default/Favicons
                  [...]

Other changes
-------------

The full list is in the `changelog <https://psutil.readthedocs.io/en/latest/changelog.html>`__.
