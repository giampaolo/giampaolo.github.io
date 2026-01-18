Title: Efficiently waiting for processes on Linux and BSD
Date: 2026-01-17
Tags: psutil, python
Authors: Giampaolo Rodola

# Efficiently waiting for processes on Linux and BSD

One of the less glamorous aspects of process management is waiting for a
process to terminate. For years, psutil's
[Process.wait()](https://psutil.readthedocs.io/en/latest/#psutil.Process.wait)
method relied on a busy-loop polling approach on POSIX systems (see
[source](https://github.com/giampaolo/psutil/blob/700b7e6a/psutil/_psposix.py#L95-L160)).
The
[subprocess](https://docs.python.org/3/library/subprocess.html#subprocess.Popen.wait)
module uses exaclty the same approach (see
[source](https://github.com/python/cpython/blob/69a9dd0187b/Lib/subprocess.py#L2050-L2088)).
The logic is: check if the process is gone with `os.waitpid()`, sleep for a
tiny interval, check again, sleep a bit longer, check again, etc.

## The problem with busy polling

- CPU wake-ups: even with exponential backoff (starting at 0.1ms, capping at
  40ms), the system constantly wakes up to check process status.
- Latency: there's always a gap between when a process actually terminates and
  when we detect it.

## The solution: event-driven waiting

All POSIX systems provide at least one mechanism to be notified when a file
descriptor becomes ready. These are
[select()](https://man7.org/linux/man-pages/man2/select.2.html),
[poll()](https://man7.org/linux/man-pages/man2/poll.2.html),
[epoll()](https://man7.org/linux/man-pages/man7/epoll.7.html) and
[kqueue()](https://man.freebsd.org/cgi/man.cgi?kqueue) system calls. Up until
now I believed they could only be used with socket file descriptors, but it
turns out they can also be used with process PIDs. As for Windows, we don't use busy loops there, as we rely on `WaitForSingleObject` (see [source](https://github.com/giampaolo/psutil/blob/700b7e6a/psutil/arch/windows/proc.c#L90-L156)).

## Linux

Linux 5.3 introduced [pidfd_open()](https://man7.org/linux/man-pages/man2/pidfd_open.2.html), which was added to the `os` module in
Python 3.9. It returns a file descriptor referencing a process PID. This can be
used in conjunction with `select()`, `poll()` or `epoll()` to effectively wait
until process exits. E.g. by using `poll()`:

```python
import os, select

pidfd = os.pidfd_open(pid, 0)
poller = select.poll()
poller.register(pidfd, select.POLLIN)
events = poller.poll(timeout_ms)  # blocks until process exits or timeout occurs
if events:
    print(f"{pid=} terminated")
else:
    raise TimeoutError
```

This approach has zero busy-looping. The kernel wakes us up exactly when the
process terminates or when the timeout expires in case the PID is still alive.

Note: I opted for `poll()` instead of `epoll()` because it does not requires an
extra file descriptor, and I expect it to be slightly faster when watching a
single FD.

Fun fact: working on this topic reminded me of a cPython bug report I opened
almost 20 years ago,
[https://bugs.python.org/issue1685000](https://bugs.python.org/issue1685000).

## macOS and BSD

BSD-derived systems (including macOS) provide `kqueue()` syscall, which is
conceptually similar, but more powerful. `kqueue()` can be passed
a PID directly:

```python
import select

kq = select.kqueue()
kev = select.kevent(
  pid,
  filter=select.KQ_FILTER_PROC,
  flags=select.KQ_EV_ADD | select.KQ_EV_ONESHOT,
  fflags=select.KQ_NOTE_EXIT,
)
events = kq.control([kev], 1, timeout)  # blocks until process exits or timeout occurs
if events:
    print(f"{pid=} terminated")
else:
    raise TimeoutError
```

## Graceful fallbacks

Both `pidfd_open()` and `kqueue()` can fail for different reasons. For example,
`pidfd_open()` may fail with `EMFILE` if the process runs out of file
descriptors. Since the default limit is often 1024, this effectively caps the
number of PIDs that can be waited on simultaneously. Likewise, according to the
man page `kqueue()` may fail with `EACCES` when registering a `KQ_FILTER_PROC`
event. In both cases, psutil silently falls back to the traditional polling
approach rather than raising an exception (see
[source](https://github.com/giampaolo/psutil/blob/700b7e6a/psutil/_psposix.py#L95-L160)).

## For the future

Another obvious candidate that could benefit from this approach is the
[psutil.wait_procs()](https://psutil.readthedocs.io/en/latest/#psutil.wait_procs)
function (see
[source](https://github.com/giampaolo/psutil/blob/700b7e6a/psutil/__init__.py#L1570-L1659)).
It allows you to wait on multiple processes, and currently relies on a busy
loop. I'll try to put together a PR for this later, though this function is
trickier to integrate in the `poll()` / `kqueue()` loops.

Also, the `pidfd_open()` limitation of 1024 file descriptors
is something to keep in mind when waiting for multiple PIDs. It consumes FDs
also for other syscalls like `open()`, and once you hit the FD limit you can't
open files, or do anything that requires a descriptor.

I also think it makes sense to apply this change both to subprocess and asyncio
modules in cPython. That's another potential PR I might work on in the future.

----

This change is available in psutil 7.2.2. See
[PR-2706](https://github.com/giampaolo/psutil/pull/2706) for the full
implementation.
