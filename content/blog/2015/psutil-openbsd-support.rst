psutil OpenBSD support
######################

:date: 2015-11-25
:tags: psutil, bsd, python

OK, this is a big one: starting from version 3.3.0 (released just now) `psutil <https://github.com/giampaolo/psutil>`__ will officially support OpenBSD platforms. This was contributed by `Landry Breuil <https://github.com/landryb>`__ (thanks dude!) and myself in `PR-615 <https://github.com/giampaolo/psutil/pull/615>`__. The interesting parts of the code changes are this and this.

Differences with FreeBSD
------------------------

As expected, OpenBSD implementation is very similar to FreeBSD's (which was already in place), that is why I decided to merge most of it in a single C file (`_psutil_bsd.c <https://github.com/giampaolo/psutil/blob/master/psutil/_psutil_bsd.c>`__) and use 2 separate C files for when the two implementations differed too much: `freebsd.c <https://github.com/giampaolo/psutil/blob/master/psutil/arch/bsd/freebsd.c>`__ and `openbsd.c <https://github.com/giampaolo/psutil/blob/master/psutil/arch/bsd/freebsd.c>`__. In terms of functionality here's the differences with FreeBSD. Unless specified, these differences are due to the kernel which does not provide the information natively (meaning we can't do anything about it).

* ``Process.memory_maps()`` is not implemented. The kernel provides the necessary pieces but I didn't do this yet (hopefully later).
* ``Process.num_ctx_switches()``'s involuntary field is always 0. `kinfo_proc <https://github.com/giampaolo/psutil/blob/fc1e59d08c968898c2ede425a621b62ccf44681c/psutil/_psutil_bsd.c#L335>`__ provides this info but it is always set to 0.
* ``Process.cpu_affinity()`` (get and set) is not supported.
* ``Process.exe()`` is determined by inspecting the command line so it may not always be available (return None).
* ``psutil.swap_memory()`` sin and sout (swap in and swap out) values are not available and hence are always set to 0.
* ``psutil.cpu_count(logical=False)`` always return None.

Similarly to FreeBSD, also OpenBSD implementation of `Process.open_files()` is problematic as it is not able to return file paths (FreeBSD can sometimes). Other than these differences the functionalities are all there and pretty much the same, so overall I'm pretty satisfied with the result.

Considerations about BSD platforms
----------------------------------

psutil has been supporting FreeBSD basically `since the beginning <https://code.google.com/p/psutil/source/detail?r=5f7c3aee0186#>`__ (year 2009). At the time it made sense to support FreeBSD instead of other BSD variants because it is the `most popular <https://en.wikipedia.org/wiki/Comparison_of_BSD_operating_systems#Popularity>`__, followed by OpenBSD and NetBSD. Compared to FreeBSD, OpenBSD appears to be more "minimal" both in terms of facilities provided by the kernel and the number of system administration tools available. One thing which I appreciate a lot about FreeBSD is that the source code of all CLI tools installed on the system is available under /usr/bin/src, which was a big help for implementing all psutil APIs. OpenBSD source code is `also available <http://cvsweb.openbsd.org/cgi-bin/cvsweb/>`__ but it uses CSV and I am not sure it includes the source code for all CLI tools. There are still two more BSD variants for which it may be worth to add support for: NetBSD and DragonflyBSD (in this order). About a year ago some guy provided a `patch <https://github.com/giampaolo/psutil/issues/429>`__ for adding basic NetBSD support so it is likely that will happen sooner or later.

Other enhancements available in this release
--------------------------------------------

The only other enhancement is `issue #558 <https://github.com/giampaolo/psutil/issues/558>`__, which allows specifying a different location of /proc filesystem on Linux.

External discussions
--------------------

* `Reddit <https://www.reddit.com/r/Python/comments/3u8wm3/openbsd_support_for_psutil_330/>`__
* `Hacker news <https://news.ycombinator.com/item?id=10628726>`__

