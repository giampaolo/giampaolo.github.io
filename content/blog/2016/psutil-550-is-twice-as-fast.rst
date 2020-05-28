psutil 5.5.0 is twice as fast
#############################

:date: 2016-11-06
:tags: psutil, python, performance, macos, bsd, sunos

OK, this is a big one. Starting from psutil 5.0.0 you can query multiple Process information around twice as fast than with previous versions (see `original ticket <https://github.com/giampaolo/psutil/issues/799>`__ and `updated doc <https://psutil.readthedocs.io/en/latest/#psutil.Process.oneshot>`__). It took me 7 months, 108 commits and a massive refactoring of psutil internals (here is the `big commit <https://github.com/giampaolo/psutil/pull/937/files>`__), and I can safely say this is one of the best improvements and long standing issues which have been addressed in a major psutil release. Here goes.

The problem
-----------

Except for some cases, the way different process information are retrieved varies depending on the OS. Sometimes it requires reading a file in /proc filesystem (Linux), some other times it requires using C (Windows, BSD, OSX, SunOS), but every time it's done differently. Psutil abstracts this complexity by providing a nice high-level interface so that you, say, call ``Process.name()`` without worrying about what happens behind the curtains or on what OS you're on.

Internally, it is not rare that multiple process info (e.g. name(), ppid(), uids(), create_time()) may be fetched by using the same routine. For example, on Linux we read /proc/stat to get the process name, terminal, CPU times, creation time, status and parent PID, but only one value is returned and the others are discarded. On Linux the code below reads /proc/stat 6 times:

.. code-block:: python

    >>> import psutil
    >>> p = psutil.Process()
    >>> p.name()
    >>> p.cpu_times()
    >>> p.create_time()
    >>> p.ppid()
    >>> p.status()
    >>> p.terminal()

Another example is BSD. In order to get process name, memory, CPU times and other metrics, a single sysctl() call is necessary, but again, because of how psutil used to work so far that same sysctl() call is executed every time (see `here <https://github.com/giampaolo/psutil/blob/2fe3f456321ca1605aaa2b71a7193de59d93075c/psutil/_psutil_bsd.c#L242-L258>`__, `here <https://github.com/giampaolo/psutil/blob/2fe3f456321ca1605aaa2b71a7193de59d93075c/psutil/_psutil_bsd.c#L261-L277>`__, and so on), one information is returned (say name()) and the rest is discarded. Not anymore.

Do it in one shot
-----------------

It appears clear how the approach described above is not efficient, also considering that applications similar to top, htop, ps or glances usually collect more than one info per-process.
psutil 5.0.0 introduces a new oneshot() context manager. When used, the internal routine is executed once (in the example below on name()) and the other values are cached. The subsequent calls sharing the same internal routine (read /proc/stat, call sysctl() or whatever) will return the cached value.
With psutil 5.0.0 the code above can be rewritten like this, and on Linux it will run 2.4 times faster:

.. code-block:: python

    >>> import psutil
    >>> p = psutil.Process()
    >>> with p.oneshot():
    ...     p.name()
    ...     p.cpu_times()
    ...     p.create_time()
    ...     p.ppid()
    ...     p.status()
    ...     p.terminal()

Implementation
--------------

One great thing about psutil design is its abstraction. It is dived in 3 "layers". The first layer is represented by the main `Process class <https://github.com/giampaolo/psutil/blob/88ea5e0b2cc15c37fdeb3e38857f6dab6fd87d12/psutil/__init__.py#L340>`__ (python), which is what dictates the end-user high-level API. The second layer is the `OS-specific Python module <https://github.com/giampaolo/psutil/blob/88ea5e0b2cc15c37fdeb3e38857f6dab6fd87d12/psutil/_pslinux.py#L1097>`__ which is thin wrapper on top of the OS-specific `C extension module <https://github.com/giampaolo/psutil/blob/88ea5e0b2cc15c37fdeb3e38857f6dab6fd87d12/psutil/_psutil_linux.c>`__ (third layer). Because this was organized this way (modularly) the refactoring was reasonably smooth. In order to do this I first refactored those C functions collecting multiple info and grouped them in a single function (e.g. see `BSD implementation <https://github.com/giampaolo/psutil/blob/88ea5e0b2cc15c37fdeb3e38857f6dab6fd87d12/psutil/_psutil_bsd.c#L198-L338>`__). Then I wrote a `decorator <https://github.com/giampaolo/psutil/blob/88ea5e0b2cc15c37fdeb3e38857f6dab6fd87d12/psutil/_common.py#L264-L314>`__ which enables the cache only when requested (when entering the context manager) and decorated the `"grouped functions" <https://github.com/giampaolo/psutil/blob/88ea5e0b2cc15c37fdeb3e38857f6dab6fd87d12/psutil/_psbsd.py#L491>`__ with with it. The whole thing is enabled on request by the highest-level `oneshot() <https://github.com/giampaolo/psutil/blob/b5582380ac70ca8c180344d9b22aacdff73b1e0b/psutil/__init__.py#L458-L518>`__ context manager, which is the only thing which is exposed to the end user. Here's the decorator:

.. code-block:: python

    def memoize_when_activated(fun):
        """A memoize decorator which is disabled by default. It can be
        activated and deactivated on request.
        """
        @functools.wraps(fun)
        def wrapper(self):
            if not wrapper.cache_activated:
                return fun(self)
            else:
                try:
                    ret = cache[fun]
                except KeyError:
                    ret = cache[fun] = fun(self)
                return ret

        def cache_activate():
            """Activate cache."""
            wrapper.cache_activated = True

        def cache_deactivate():
            """Deactivate and clear cache."""
            wrapper.cache_activated = False
            cache.clear()

        cache = {}
        wrapper.cache_activated = False
        wrapper.cache_activate = cache_activate
        wrapper.cache_deactivate = cache_deactivate
        return wrapper

In order to measure the various speedups I finally wrote a `benchmark script <https://github.com/giampaolo/psutil/blob/b5582380ac70ca8c180344d9b22aacdff73b1e0b/scripts/internal/bench_oneshot.py>`__ (well, `two <https://github.com/giampaolo/psutil/blob/b5582380ac70ca8c180344d9b22aacdff73b1e0b/scripts/internal/bench_oneshot_2.py>`__ actually) and kept tuning until I was sure the various changes made psutil actually faster. The benchmark scripts calculate the speedup you can get if you call all the "grouped" methods together (best case scenario).

Linux: +2.56x speedup
---------------------

Linux process is the only pure-python implementation as (almost) all process info are gathered by reading files in the /proc filesystem. /proc files typically contain different information about the process and /proc/PID/stat and /proc/PID/status are the perfect examples. That's why on Linux we aggregate them in 3 groups. The relevant part of the Linux implementation can be seen `here <https://github.com/giampaolo/psutil/blob/b5582380ac70ca8c180344d9b22aacdff73b1e0b/psutil/_pslinux.py#L1108-L1153>`__.

Windows: from +1.9x to +6.5x speedup
------------------------------------

Windows is an interesting one. In normal circumstances, if we're querying a process owned by our user, we group together only process' num_threads(), num_ctx_switches() and num_handles(), getting a +1.9x speedup if we access those methods in one shot. Windows is particular though, because certain methods use a `dual implementation <https://github.com/giampaolo/psutil/issues/304>`__: a "fast method" is attempted first, but if the process is owned by another user it fails with AccessDenied. In that case psutil falls back on using a second "slower" method (see `here <https://github.com/giampaolo/psutil/blob/0ccd1373c6e7a189e095df5c436568fb1e8b4d14/psutil/_pswindows.py#L681>`__ for example).
The second method is slower because it `iterates over all PIDs <https://github.com/giampaolo/psutil/blob/0ccd1373c6e7a189e095df5c436568fb1e8b4d14/psutil/arch/windows/process_info.c#L790>`__ but differently than "plain" Windows APIs it can be used to `get multiple info in one shot <https://github.com/giampaolo/psutil/blob/0ccd1373c6e7a189e095df5c436568fb1e8b4d14/psutil/_psutil_windows.c#L2789>`__: num threads, context switches, handles, CPU times, create time and IO counters. That is why querying processes owned by other users results in an impressive +6.5 speedup.

OSX: +1.92x speedup
-------------------

On OSX we can get 2 groups of information. With `sysctl() <https://github.com/giampaolo/psutil/blob/0ccd1373c6e7a189e095df5c436568fb1e8b4d14/psutil/_psutil_osx.c#L129>`__ syscall we get process parent PID, uids, gids, terminal, create time, name. With `proc_info() <https://github.com/giampaolo/psutil/blob/0ccd1373c6e7a189e095df5c436568fb1e8b4d14/psutil/_psutil_osx.c#L183>`__ syscall we get CPU times (for PIDs owned by another user) memory metrics and ctx switches. Not bad.

BSD: +2.18x speedup
-------------------

BSD was an interesting one as we gather a tons of process info just by calling sysctl() (see `implementation <https://github.com/giampaolo/psutil/blob/0ccd1373c6e7a189e095df5c436568fb1e8b4d14/psutil/_psutil_bsd.c#L199>`__). In a single shot we get process name, ppid, status, uids, gids, IO counters, CPU and create times, terminal and ctx switches.

SunOS: +1.37 speedup
--------------------

SunOS implementation is similar to Linux implementation in that it reads files in /proc filesystem but differently from Linux this is done in C. Also in this case, we can group different metrics together (see `here <https://github.com/giampaolo/psutil/blob/b5582380ac70ca8c180344d9b22aacdff73b1e0b/psutil/_psutil_sunos.c#L83-L142>`__ and `here <https://github.com/giampaolo/psutil/blob/b5582380ac70ca8c180344d9b22aacdff73b1e0b/psutil/_psutil_sunos.c#L171-L189>`__).

External links
--------------

* `reddit <https://www.reddit.com/r/Python/comments/5bhn4q/psutil_500_is_around_twice_as_fast/>`__



