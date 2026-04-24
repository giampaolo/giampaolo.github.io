Announcing psutil 2.0
#####################

:date: 2014-03-10
:tags: psutil, python, api-design
:slug: psutil-20

`psutil <https://github.com/giampaolo/psutil/>`__ 2.0 is out. This is a major rewrite and reorganization of both the Python and C extension modules. It costed me four months of work and more than **22,000 lines** (the diff against old 1.2.1). Many of the changes are not backward compatible; I'm sure this will cause some pain, but I think it's for the better and needed to be done.

API changes
-----------

I already wrote a detailed `blog post <psutil-20-api-redesign>`_ about this, so use that as the official reference on how to port your code.

RST documentation
-----------------

I've never been happy with the old doc hosted on Google Code. The markup language provided by Google is pretty limited, plus it's not under revision control. The new doc is more detailed, uses reStructuredText as the markup language, lives in the same code repository as psutil, and is hosted on the excellent Read the Docs: http://psutil.readthedocs.org/

Physical CPUs count
-------------------

You're now able to distinguish between logical and physical CPUs. The full story is in `#427 <https://github.com/giampaolo/psutil/issues/427>`__.

.. code-block:: pycon

    >>> psutil.cpu_count()  # logical
    4
    >>> psutil.cpu_count(logical=False)  # physical cores only
    2

Process instances are hashable
------------------------------

``psutil.Process`` instances can now be compared for equality and used in sets and dicts. The most useful application is diffing process snapshots:

.. code-block:: pycon

    >>> before = set(psutil.process_iter())
    >>> # ... some time passes ...
    >>> after = set(psutil.process_iter())
    >>> new_procs = after - before  # processes spawned in between

Equality is not just PID-based. It also includes the process creation time, so a ``Process`` whose PID got reused by the kernel won't be mistaken for the original. The full story is in `#452 <https://github.com/giampaolo/psutil/issues/452>`__.

Speedups
--------

* `#477 <https://github.com/giampaolo/psutil/issues/477>`__: ``Process.cpu_percent()`` is about 30% faster.
* `#478 <https://github.com/giampaolo/psutil/issues/478>`__: (Linux) almost all APIs are about 30% faster on Python 3.X.

Other improvements and bugfixes
-------------------------------

* `#424 <https://github.com/giampaolo/psutil/issues/424>`__: published Windows installers for Python 3.X 64-bit.
* `#447 <https://github.com/giampaolo/psutil/issues/447>`__: the ``psutil.wait_procs()`` ``timeout`` parameter is now optional.
* `#459 <https://github.com/giampaolo/psutil/issues/459>`__: a `Makefile <https://github.com/giampaolo/psutil/blob/v2.0.0/Makefile>`__ is now available for running tests and other repetitive tasks (also on Windows).
* `#463 <https://github.com/giampaolo/psutil/issues/463>`__: the ``timeout`` parameter of ``cpu_percent*`` functions defaults to 0.0, because the previous default was a common source of slowdowns.
* `#340 <https://github.com/giampaolo/psutil/issues/340>`__: (Windows) ``Process.open_files()`` no longer hangs.
* `#448 <https://github.com/giampaolo/psutil/issues/448>`__: (Windows) fixed a memory leak affecting ``Process.children()`` and ``Process.ppid()``.
* `#461 <https://github.com/giampaolo/psutil/issues/461>`__: namedtuples are now pickle-able.
* `#474 <https://github.com/giampaolo/psutil/issues/474>`__: (Windows) ``Process.cpu_percent()`` is no longer capped at 100%.
