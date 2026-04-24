Removing Process.memory_maps() on macOS
#######################################

:date: 2019-03-05
:tags: psutil, python, macos, api-design
:slug: removing-processmemory_maps-on-macos

This is part of the psutil 5.6.0 release (see the full `release notes <psutil-560-and-process-parents>`_).

As of 5.6.0, ``Process.memory_maps()`` is no longer defined on macOS.

The bug
-------

`#1291 <https://github.com/giampaolo/psutil/issues/1291>`__: on macOS, ``Process.memory_maps()`` would either raise ``OSError: [Errno 22] Invalid argument`` or segfault the whole Python process! Both triggered from code as simple as ``psutil.Process().as_dict()``, since ``Process.as_dict()`` iterates every attribute, and ``Process.memory_maps()`` is one of them.

The root cause was inside Apple's undocumented ``proc_regionfilename()`` syscall. On some memory regions it returns ``EINVAL``. On others it takes the process down. Which regions? Nobody figured out. Arnon Yaari (`@wiggin15 <https://github.com/wiggin15>`__) did most of the investigation: he wrote a `standalone C reproducer <https://gist.github.com/wiggin15/0a4c51b5bc6c52e6e31e2234f88558ab>`__ and walked me through what he'd tried.

In `PR-1436 <https://github.com/giampaolo/psutil/pull/1436>`__ I attempted a fix by reverse-engineering ``vmmap(1)`` but it didn't work. The fundamental problem is that ``vmmap`` is closed source and ``proc_regionfilename`` is undocumented. Neither my virtualized macOS (10.11.6) nor Travis CI (10.12.1) could reproduce the bug, which reproduced reliably only on 10.14.3.

Why remove outright
-------------------

While removing the C code I noticed that the macOS unit test had been disabled long ago, presumably by me after recurring flaky Travis runs. Meaning that the method had been broken on some macOS versions far longer than the 2018 bug report suggested.

Deprecating for a cycle didn't help either: raising ``AccessDenied`` breaks code that relied on a successful return, returning an empty list does the same silently, and leaving the method in place doesn't stop the segfault. Basically there was no sane solution, so since 5.6 is a major version I decided to just remove ``Process.memory_maps()`` for good.

On macOS it never supported other processes anyway. Calling it on any PID other than the current one (or its children) raised ``AccessDenied``, even as root.

If someone finds a Mach API path that works, the method can return. Nobody has found one so far.
