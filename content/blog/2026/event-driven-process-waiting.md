Title: From Python 3.3 to today: ending 15 years of subprocess polling
Slug: event-driven-process-waiting
Date: 2026-01-17
Tags: psutil, python, python-core, async
Authors: Giampaolo Rodola

One of the less glamorous aspects of process management is waiting for a
process to terminate. The standard library's **subprocess** module has relied
on a busy-loop polling approach since the *timeout* parameter was added to
[Popen.wait()](https://docs.python.org/3/library/subprocess.html#subprocess.Popen.wait)
in Python 3.3, around 15 years ago (see
[commit](https://github.com/python/cpython/commit/31aa7dd14196)). And psutil's
[Process.wait()](https://psutil.readthedocs.io/en/latest/#psutil.Process.wait)
method used exactly the same technique (see
[source](https://github.com/giampaolo/psutil/blob/700b7e6a/psutil/_psposix.py#L95-L160)).

The logic is straightforward: check whether the process has exited using
non-blocking `waitpid(WNOHANG)`, sleep briefly, check again, sleep a bit
longer, and so on.

In this blog post I'll show how I finally addressed this long-standing
inefficiency, first in psutil, and most excitingly, directly in CPython's
standard library subprocess module.

## The problem with busy-polling

- CPU wake-ups: even with exponential backoff (starting at 0.1ms, capping at
  40ms), the system constantly wakes up to check process status, wasting CPU
  cycles and draining batteries.
- Latency: there's always a gap between when a process actually terminates and
  when you detect it.
- Scalability: monitoring many processes simultaneously magnifies all of the
  above.

## Event-driven waiting

All POSIX systems provide at least one mechanism to be notified when a file
descriptor becomes ready. These are
[select()](https://man7.org/linux/man-pages/man2/select.2.html),
[poll()](https://man7.org/linux/man-pages/man2/poll.2.html),
[epoll()](https://man7.org/linux/man-pages/man7/epoll.7.html) and
[kqueue()](https://man.freebsd.org/cgi/man.cgi?query=kqueue) system calls.
Until recently, I believed they could only be used with file descriptors
referencing sockets, pipes, etc., but it turns out they can also be used to
wait for events on process PIDs!

## Linux

Linux 5.3 introduced a new syscall,
**[pidfd_open()](https://man7.org/linux/man-pages/man2/pidfd_open.2.html)**,
which was added to the `os` module in Python 3.9. It returns a file descriptor
referencing a process PID. The interesting thing is that `pidfd_open()` can be
used in conjunction with `select()`, `poll()` or `epoll()` to effectively wait
until process exits. E.g. by using `poll()`:

```python
import os, select

pidfd = os.pidfd_open(pid, 0)
poller = select.poll()
poller.register(pidfd, select.POLLIN)
# block for 10 secs, until process exits or timeout occurs
events = poller.poll(10_000)
if events:
    print(f"{pid=} terminated")
else:
    raise TimeoutError
```

This approach has zero busy-looping. The kernel wakes us up exactly when the
process terminates or when the timeout expires if the PID is still alive.

Note: I opted for `poll()` instead of `epoll()` because it does not require an
extra file descriptor. Plus it only requires 1 syscall, so I expect it to be
slightly faster when watching a single FD instead of many.

## macOS and BSD

BSD-derived systems (including macOS) provide the `kqueue()` syscall. It's
conceptually similar to `select()`, `poll()` and `epoll()`, but more powerful
(e.g. it also handles regular files other than sockets). `kqueue()` can be
passed a PID directly, and it will return once the PID disappears or the
timeout expires:

```python
import select

kq = select.kqueue()
kev = select.kevent(
  pid,
  filter=select.KQ_FILTER_PROC,
  flags=select.KQ_EV_ADD | select.KQ_EV_ONESHOT,
  fflags=select.KQ_NOTE_EXIT,
)
# block for 10 secs, until process exits or timeout occurs
events = kq.control([kev], 1, 10)
if events:
    print(f"{pid=} terminated")
else:
    raise TimeoutError
```

## Graceful fallbacks

Both `pidfd_open()` and `kqueue()` can fail for different reasons. For example,
with `EMFILE` if the process runs out of file descriptors (usually 1024), or
with `EACCES` / `EPERM` if the syscall is explicitly blocked at the system
level (e.g. via SECCOMP). In all cases, psutil silently falls back to the
traditional busy-loop polling approach rather than raising an exception.

This fast-path-with-fallback approach is similar in spirit to
[https://bugs.python.org/issue33671](https://bugs.python.org/issue33671), where
I sped up `shutil.copyfile()` by using zero-copy system calls back in 2018. In
there `os.sendfile()` is attempted first, and if it fails (e.g. on network
filesystems) we fall back to the traditional `read()` / `write()` approach.

## Measurement

As a simple experiment, here's a simple program which waits on itself for 10
seconds without terminating:

```python
# test.py
import psutil, os
try:
    psutil.Process(os.getpid()).wait(timeout=10)
except psutil.TimeoutExpired:
    pass
```

We can measure the CPU context switching using `/usr/bin/time -v`. Before the
patch (the busy-loop):

```
$ /usr/bin/time -v python3 test.py 2>&1 | grep context
    Voluntary context switches: 258
    Involuntary context switches: 4
```

After the patch (event-driven):

```
$ /usr/bin/time -v python3 test.py 2>&1 | grep context
    Voluntary context switches: 2
    Involuntary context switches: 1
```

This shows that instead of spinning in userspace, the process blocks in
`poll()` / `kqueue()`, and is woken up only when the kernel notifies it,
resulting in just a few CPU context switches.

## CPython contribution

After landing the psutil implementation, I took the extra step and submitted a
matching pull request directly to CPython:
[cpython/PR-144047](https://github.com/python/cpython/pull/144047).

I'm especially proud of this one: this is the **second time** in psutil's 17+
year history that a feature developed in psutil made its way upstream into the
Python standard library. The first was back in 2011 (see [python-ideas ML
proposal](https://mail.python.org/pipermail/python-ideas/2011-June/010480.html)),
when `psutil.disk_usage()` inspired
[shutil.disk_usage()](https://docs.python.org/3/library/shutil.html#shutil.disk_usage).

*Funny thing:* 15 years ago, Python 3.3 added the *timeout* parameter to
`subprocess.Popen.wait()` (see
[commit](https://github.com/python/cpython/commit/31aa7dd1419)). That's
probably where I took inspiration when I first added the *timeout* parameter to
psutil's `Process.wait()` around the same time. Now, 15 years later, I'm
contributing back a similar improvement for that very same parameter.

## Implementation

This change is available in psutil 7.2.2. See
[psutil/PR-2706](https://github.com/giampaolo/psutil/pull/2706) for the full
implementation.
