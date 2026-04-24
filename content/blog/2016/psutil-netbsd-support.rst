NetBSD support
##############

:date: 2016-02-25
:tags: psutil, bsd, python
:slug: psutil-netbsd-support

Roughly two months have passed since I last `announced <../2015/psutil-openbsd-support>`_ that `psutil <https://github.com/giampaolo/psutil>`__ added support for OpenBSD. Today I'm happy to announce that it's the turn of NetBSD! This was contributed by `Thomas Klausner <https://github.com/0-wiz-0>`_, `Ryo Onodera <https://github.com/ryoon>`_ and myself in `PR-557 <https://github.com/giampaolo/psutil/pull/557>`__.

Differences with FreeBSD (and OpenBSD)
--------------------------------------

The NetBSD implementation has limitations similar to the ones I encountered with OpenBSD. Again, FreeBSD remains the BSD variant with the best support in terms of kernel functionality.

* ``Process.memory_maps()`` is not implemented. The kernel provides the necessary pieces, but I haven't done this yet (hopefully later).
* ``Process.num_ctx_switches()``'s ``involuntary`` field is always 0. The ``kinfo_proc()`` syscall provides this info, but it's always set to 0.
* ``Process.cpu_affinity()`` (get and set) is not supported.
* ``psutil.cpu_count(logical=False)`` always returns ``None``.

As for the rest: it is all there. All memory, disk, network and process APIs are fully supported and functioning.

Other enhancements available in this psutil release
---------------------------------------------------

Besides NetBSD support, this release has a couple of interesting enhancements:

* `#708 <https://github.com/giampaolo/psutil/issues/708>`__: [Linux] ``psutil.net_connections()`` and ``Process.connections()`` can be up to 3x faster when there are many connections.
* `#718 <https://github.com/giampaolo/psutil/issues/718>`__: ``psutil.process_iter()`` is now thread safe.

You can read the rest in the `changelog <https://psutil.readthedocs.io/en/latest/#id23>`__, as usual.

Move to Prague
--------------

As a personal note I'd like to add that I'm currently in Prague (Czech Republic) and I'm thinking about moving down here for a while.

Discussion
----------

* `Reddit <https://www.reddit.com/r/Python/comments/4131q2/netbsd_support_for_psutil/>`_
* `Hacker News <https://news.ycombinator.com/item?id=10909101>`_
