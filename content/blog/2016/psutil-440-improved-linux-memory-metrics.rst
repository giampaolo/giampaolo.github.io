psutil 4.4.0: improved Linux memory metrics
###########################################

:date: 2016-10-23
:tags: psutil, memory

OK, here's another `psutil <https://github.com/giampaolo/psutil>`__ release. Main highlights of this release are more accurate memory metrics on Linux and different OSX fixes. Here goes.

Linux virtual memory
--------------------

This new release sets a milestone regarding ``virtual_memory()`` metrics on Linux which are now calculated way `more precisely <https://github.com/giampaolo/psutil/issues/887>`__ (see `commit <https://github.com/giampaolo/psutil/pull/890/files>`__). Across the years different people complained that the numbers reported by virtual_memory() were not accurate or did not match the ones reported by "free" command line utility exactly (see `#862 <https://github.com/giampaolo/psutil/issues/862>`__, `#685 <https://github.com/giampaolo/psutil/issues/685>`__, `#538 <https://github.com/giampaolo/psutil/issues/538>`__). As such I investigated how "available memory" is calculated on Linux and indeed psutil were doing it wrong. It turns out "free" cmdline itself, and many other similar tools, also did it wrong up until `2 years ago <https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=34e431b0ae398fc54ea69ff85ec700722c9da773>`__ when somebody finally decided to accurately calculate the available system memory straight into the Linux kernel and expose this info to user-level applications. Starting from Linux kernel 3.14, a new "MemAvailable" column was added to /proc/meminfo and this is how psutil now determines available memory. Because of this both "available" and "used" memory fields returned by virtual_memory() precisely match "free" command line utility. As for older kernels (< 3.14), psutil tries to determine this value by using the `same algorithm <https://github.com/giampaolo/psutil/blob/a5beb29488fe75c858d30a00044cbd29d3ed3d8b/psutil/_pslinux.py#L291>`__ which was used in the original `Linux kernel commit <https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=34e431b0ae398fc54ea69ff85ec700722c9da773>`__. Free cmdline utility source code also inspired an additional fix which prevents available memory overflowing total memory on `LCX containers <https://github.com/giampaolo/psutil/blob/a5beb29488fe75c858d30a00044cbd29d3ed3d8b/psutil/_pslinux.py#L435>`__.

OSX fixes
---------

For many years the OSX development of psutil occurred on a very old OSX 10.5 version, which I emulated via VirtualBox. The OS itself was a hacked version of OSX, called iDeneb. After many years I finally managed to get access to a more recent version of OSX (El Captain) thanks to VirtualBox + Vagrant. With this I finally had the chance to address many long standing OSX bugs. Here's the list:

* `514 <https://github.com/giampaolo/psutil/issues/514>`__: fix ``Process.memory_maps()`` segfault (critical!).
* `783 <https://github.com/giampaolo/psutil/issues/783>`__: ``Process.status()`` may erroneously return "running" for zombie processes.
* `908 <https://github.com/giampaolo/psutil/issues/908>`__: different process methods could erroneously mask the real error for high-privileged PIDs and raise NoSuchProcess and ``AccessDenied`` instead of ``OSError`` and ``RuntimeError``.
* `909 <https://github.com/giampaolo/psutil/issues/909>`__: ``Process.open_files()`` and ``Process.connections()`` methods may raise ``OSError`` with no exception set if process is gone.
* `916 <https://github.com/giampaolo/psutil/issues/916>`__: fix many compilation warnings.

Improved procinfo.py script
---------------------------

`procinfo.py <https://github.com/giampaolo/psutil/blob/master/scripts/procinfo.py>`__ is a script which shows psutil capabilities regarding obtaining different info about processes. I improved it so that now it reports a lot more info. Here's a sample output:

::

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

NIC netmask on Windows
----------------------

``net_if_addrs()`` on Windows is now able to return the netmask.

Other improvements and bug fixes
--------------------------------

Just take a look at the `HISTORY <https://github.com/giampaolo/psutil/blob/master/HISTORY.rst#440---2016-10-23>`__ file.
