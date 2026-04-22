Improved process_iter()
#######################

:date: 2017-09-03
:tags: psutil, python, process_iter

This is part of the `psutil 5.3.0 release </blog/2017/psutil-530.html>`__ (see the `changelog <https://psutil.readthedocs.io/latest/changelog.html>`__ for the full list of changes).

The old pattern
---------------

Iterating over processes and collecting attributes requires more boilerplate than it should. A process returned by `process_iter() <https://psutil.readthedocs.io/en/latest/#psutil.process_iter>`__ may disappear before you access it, or require elevated privileges, so every lookup has to be guarded with a ``try / except``:

.. code-block:: python

    >>> import psutil
    >>> for proc in psutil.process_iter():
    ...     try:
    ...         pinfo = proc.as_dict(attrs=['pid', 'name'])
    ...     except (psutil.NoSuchProcess, psutil.AccessDenied):
    ...         pass
    ...     else:
    ...         print(pinfo)
    ...
    {'pid': 1, 'name': 'systemd'}
    {'pid': 2, 'name': 'kthreadd'}
    {'pid': 3, 'name': 'ksoftirqd/0'}

This is not decorative. It's necessary to avoid the race condition.

The new pattern
---------------

5.3.0 adds ``attrs`` and ``ad_value`` parameters to ``process_iter()``. With these, the loop body becomes:

.. code-block:: python

    >>> import psutil
    >>> for proc in psutil.process_iter(attrs=['pid', 'name']):
    ...     print(proc.info)
    ...
    {'pid': 1, 'name': 'systemd'}
    {'pid': 2, 'name': 'kthreadd'}
    {'pid': 3, 'name': 'ksoftirqd/0'}

Internally, ``process_iter()`` attach an ``info`` dict to the ``Process`` instance. The attributes are pre-fetched in one shot. Processes that disappear during iteration are silently skipped, and attributes that would raise ``AccessDenied`` gets assigned ``ad_value``, which defaults to ``None``:

.. code-block:: python

    for p in psutil.process_iter(['name', 'username'], ad_value="N/A"):
        print(p.name(), p.username())

Performance
-----------

Beyond the syntactic win, the new syntax is also faster than calling individual methods in a loop. ``process_iter(attrs=[...])`` is equivalent to using `Process.oneshot() <https://psutil.readthedocs.io/en/latest/#psutil.Process.oneshot>`__ on each process (see `One shot, twice as fast </blog/2016/psutil-550-is-twice-as-fast.html>`__ for how that works): attributes that share a syscall or a ``/proc`` file are fetched together instead of re-read on every method call, which is a lot faster.

Comprehensions
--------------

With the exception boilerplate out of the way, comprehensions finally work cleanly. E.g. getting processes owned by the current user can be written as:

.. code-block:: python

    >>> import getpass
    >>> from pprint import pprint as pp
    >>> pp([(p.pid, p.info['name']) for p in psutil.process_iter(attrs=['name', 'username']) if p.info['username'] == getpass.getuser()])
    [(16832, 'bash'),
     (19772, 'ssh'),
     (20492, 'python')]
