psutil NetBSD support
#####################

:date: 2016-02-25
:tags: psutil, bsd, python

Roughly two months have passed since I last announced `psutil`_ added support for OpenBSD platforms. Today I am happy to announce we also have NetBSD support! This was contributed by `Thomas Klausner <https://github.com/0-wiz-0>`_, `Ryo Onodera <https://github.com/ryoon>`_ and myself in PR `#570 <https://github.com/giampaolo/psutil/pull/557>`_.

Differences with FreeBSD (and OpenBSD)
--------------------------------------

NetBSD implementation has similar limitations as the ones I encountered with OpenBSD. Again, FreeBSD presents itself as the BSD variant with the best support in terms of kernel functionalities.

* ``Process.memory_maps()`` is not implemented. The kernel provides the necessary pieces but I didn't do this yet (hopefully later).
* ``Process.num_ctx_switches()``'s involuntary field is always 0. ``kinfo_proc`` syscall provides this info but it is always set to 0.
* ``Process.cpu_affinity()`` (get and set) is not supported.
* ``psutil.cpu_count(logical=False)`` always return ``None``.

As for the rest: it is all there. All memory, disk, network and process APIs are fully supported and functioning.

Other enhancements available in this psutil release
---------------------------------------------------

Other than NetBSD support this new release has a couple of interesting enhancements:

* `#708 <https://github.com/giampaolo/psutil/issues/708>`_: [Linux] ``psutil.net_connections()`` and ``Process.connections()`` on Python can be up to 3x faster in case of many connections.
* `#718 <https://github.com/giampaolo/psutil/issues/718>`_: ``process_iter()`` is now thread safe.

You can read the rest in the `HISTORY <https://github.com/giampaolo/psutil/blob/master/HISTORY.rst>`_ file, as usual.

Move to Prague
--------------

As a personal note I'd like to add that I'm currently in Prague (Czech Republic) and I'm thinking about moving down here for a while. The city is great and girls are beautiful. ;-)

External discussions
--------------------

* `reddit <https://www.reddit.com/r/Python/comments/4131q2/netbsd_support_for_psutil/>`_
* `hackernews <https://news.ycombinator.com/item?id=10909101>`_

.. _`psutil`: https://github.com/giampaolo/psutil
