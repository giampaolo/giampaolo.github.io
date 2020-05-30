psutil 5.6.0 and process parents
################################

:date: 2019-03-05
:tags: psutil

Hello world =)

It was a long time since my last blog post (over 1 year and a half). During this time I moved between Italy, Prague and Shenzhen (China), and also contributed a couple of nice patches for Python I want to blog about when Python 3.8 will be out: zero-copy for `shutil.copy() <https://bugs.python.org/issue33671>`__ functions and `socket.create_server() <https://github.com/python/cpython/pull/11784>`__ utility function. But let's move on and talk about what this blog post is about: the next major psutil version.

Process parents()
-----------------

From the doc: return the parents of this process as a list of Process instances. If no parents are known return an empty list.

.. code-block:: python

    >>> import psutil
    >>> p = psutil.Process(5312)
    >>> p.parents()
    [psutil.Process(pid=4699, name='bash', started='09:06:44'),
     psutil.Process(pid=4689, name='gnome-terminal-server', started='0:06:44'),
     psutil.Process(pid=1, name='systemd', started='05:56:55')]

Nothing really new here, as it's a convenience method based on the existing `parent() <https://psutil.readthedocs.io/en/latest/#psutil.Process.parent>`__ method, but still it's something nice to have implemented as a builtin and which can be used to work with process trees in conjunction with `children() <https://psutil.readthedocs.io/en/latest/#psutil.Process.children>`__ method. The idea was proposed by Ghislain Le Meur.

Windows
-------

A bunch of interesting improvements occurred on Windows.

The first one is that certain Windows APIs requiring to be dynamically loaded from DLL libraries are now loaded only once on startup (instead of on per function call), significantly speeding up different functions and methods. This is described and implemented in PR `#1422 <https://github.com/giampaolo/psutil/pull/1422>`__ which also provides benchmarks.

Another one is Process' `suspend() <https://psutil.readthedocs.io/en/latest/#psutil.Process.suspend>`__ and `resume() <https://psutil.readthedocs.io/en/latest/#psutil.Process.resume>`__ methods. Before they were using CreateToolhelp32Snapshot() to iterate over all process' threads which was somewhat unorthodox and didn't work if process was suspended via Process Hacker. Now it relies on undocumented NtSuspendProcess and NtResumeProcess APIs, which is the same approach used by ProcessHacker and other famous Sysinternals tools. The change was proposed and discussed in issue `#1379 <https://github.com/giampaolo/psutil/issues/1379>`__ and implemented in PR `#1435 <https://github.com/giampaolo/psutil/pull/1435>`__. I think I will later propose the addition of suspend() and resume() method in subprocess module in Python.

Last nice improvement about Windows it's about SE DEBUG mode. SE DEBUG mode can be seen as a "bit" which you can set on the Python process on startup so that we have more chances of querying processes owned by other users, including many owned by Administrator and Local System. Practically speaking this means we will get less AccessDenied exceptions for low PID processes.  It turns out the code doing this has been broken presumably for years, and never set SE DEBUG. This is fixed now and the change was made in PR `#1429 <https://github.com/giampaolo/psutil/pull/1429>`__.

Removal of Process.memory_maps() on OSX
---------------------------------------

This was somewhat `controversial <https://github.com/giampaolo/psutil/issues/1291>`__. The history about memory_maps() on OSX is a painful one. It was based on an undocumented and probably broken Apple API called proc_regionfilename() which made memory_maps() either randomly raise EINVAL or result in segfault! Also, memory_maps() could only be used for the current process, limiting its usefulness to os.getpid() only. For any other process it raised AccessDenied. This has been a known problem for a long time but sometime over the last few years I got tired of seeing random test failures on Travis that I couldn't reproduce locally, so I commented the unit-test and forget about it until last week, when I realized the real impact this has on production code. I tried looking for a solution once again, spending quite some time looking for public source codes which managed to do this right with no luck. The only tool I'm aware of which does this right is vmmap from Apple, but it's closed source. After careful thinking, since no solution was found, I decided to just remove memory_maps() from OSX. This is not something I took lightly, but considering the alternative is getting a segfault I decided to sacrifice backward compatibility (hence the major version bump).

Improved exceptions
-------------------

One problem which afflicted psutil maintenance over the years was receiving bug reports including tracebacks which didn't provide any information on what syscall failed exactly. This was especially painful on Windows where a single routine can invoke different Windows APIs. Now the OSError (or WindowsError) exception will include the syscall from which the error originated, see `PR-#1428 <https://github.com/giampaolo/psutil/pull/1428>`__.

Other important bugfixes
------------------------

* `#1353 <https://github.com/giampaolo/psutil/issues/1353>`__: process_iter() is now thread safe
* `#1411 <https://github.com/giampaolo/psutil/issues/1411>`__: [BSD]segfault could occur on Process instantiation
* `#1427 <https://github.com/giampaolo/psutil/issues/1427>`__: [OSX] Process cmdline() and environ() may erroneously raise OSError on failed malloc().
* `#1447 <https://github.com/giampaolo/psutil/issues/1447>`__: original exception wasn't turned into NoSuchProcess / AccessDenied exceptions when using Process.oneshot() ctx manager.

A full list of enhancements and bug fixes is available `here <https://github.com/giampaolo/psutil/blob/master/HISTORY.rst#560>`__.

