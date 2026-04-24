Proper zombie process handling
##############################

:date: 2015-06-13
:tags: psutil, python, api-design
:slug: zombie-processes

This is part of the psutil 3.0 release (see the full `release notes <psutil-30-reimplement-ifconfig-in-python>`_).

Except on Linux and Windows (which does not have them), support for `zombie processes <http://askubuntu.com/a/48625>`__ was broken. The full story is in `#428 <https://github.com/giampaolo/psutil/issues/428>`__.

The problem
-----------

Say you create a zombie process and instantiate a ``Process`` for it:

.. code-block:: python

    import os, time

    def create_zombie():
        pid = os.fork()  # the zombie
        if pid == 0:
            os._exit(0)  # child exits immediately
        else:
            time.sleep(1000)  # parent does NOT call wait()

    pid = create_zombie()
    p = psutil.Process(pid)

Up until psutil 2.X, every time you tried to query it you'd get a ``NoSuchProcess`` exception:

.. code-block:: pycon

    >>> p.name()
      File "psutil/__init__.py", line 374, in _init
        raise NoSuchProcess(pid, None, msg)
    psutil.NoSuchProcess: no process found with pid 123

This was misleading, because the PID technically still existed:

.. code-block:: pycon

    >>> psutil.pid_exists(p.pid)
    True

Depending on the platform, some process information could still be retrieved:

.. code-block:: pycon

    >>> p.cmdline()
    ['python']

Worst of all, ``psutil.process_iter()`` didn't return zombies at all. That was a real problem, because identifying them is a legitimate use case: a zombie usually indicates a bug where a parent process spawns a child, kills it, but never calls ``wait()`` to reap it.

What changed
------------

* A new ``ZombieProcess`` exception is raised whenever a process cannot be queried because it is a zombie.
* It replaces ``NoSuchProcess``, which was incorrect and misleading.
* ``ZombieProcess`` inherits from ``NoSuchProcess``, so existing code keeps working.
* ``psutil.process_iter()`` now correctly includes zombie processes, so you can reliably identify them:

.. code-block:: python

    import psutil

    zombies = []
    for p in psutil.process_iter():
        try:
            if p.status() == psutil.STATUS_ZOMBIE:
                zombies.append(p)
        except psutil.NoSuchProcess:
            pass
