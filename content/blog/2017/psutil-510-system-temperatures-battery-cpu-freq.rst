psutil 5.1.1 system temperature, battery and CPU frequency
##########################################################

:date: 2017-02-01
:tags: psutil, python

OK, here's another `psutil <https://github.com/giampaolo/psutil/>`__ release. Main highlights of this release are sensors-related APIs.

Temperatures
------------

It is now possible to retrieve hardware temperatures. The relevant commit is `here <https://github.com/giampaolo/psutil/pull/962/files>`__. Unfortunately this is Linux only. I couldn't manage to implement this on other platforms mainly for two reasons:

* On Windows it is hard to do this in a hardware agnostic fashion. I bumped into 3 different approaches, all using WMI, and none of them worked with my hardware so I gave up.
* On OSX it appears it is possible to retrieve temperatures relatively easy, but I have a virtualized OSX box which does not support sensors, so basically I gave up on this due to lack of hardware. If somebody wants to give it a try `be my guest <https://github.com/giampaolo/psutil/issues/371#issuecomment-274961948>`__.

.. code-block:: python

    >>> import psutil
    >>> psutil.sensors_temperatures()
    {'acpitz': [shwtemp(label='', current=47.0, high=103.0, critical=103.0)],
     'asus': [shwtemp(label='', current=47.0, high=None, critical=None)],
     'coretemp': [shwtemp(label='Physical id 0', current=52.0, high=100.0, critical=100.0),
                  shwtemp(label='Core 0', current=45.0, high=100.0, critical=100.0),
                  shwtemp(label='Core 1', current=52.0, high=100.0, critical=100.0),
                  shwtemp(label='Core 2', current=45.0, high=100.0, critical=100.0),
                  shwtemp(label='Core 3', current=47.0, high=100.0, critical=100.0)]}

Battery status
--------------

This works on Linux, Windows and FreeBSD and provides battery status information. The relevant commit is `here <https://github.com/giampaolo/psutil/pull/963/files>`__.

.. code-block:: python

    >>> import psutil
    >>>
    >>> def secs2hours(secs):
    ...     mm, ss = divmod(secs, 60)
    ...     hh, mm = divmod(mm, 60)
    ...     return "%d:%02d:%02d" % (hh, mm, ss)
    ...
    >>> battery = psutil.sensors_battery()
    >>> battery
    sbattery(percent=93, secsleft=16628, power_plugged=False)
    >>> print("charge = %s%%, time left = %s" % (batt.percent, secs2hours(batt.secsleft)))
    charge = 93%, time left = 4:37:08

CPU frequency
-------------

Available under Linux, Windows and OSX. Relevant commit is `here <https://github.com/giampaolo/psutil/pull/952/files>`__. Linux is the only platform which reports the real-time value (always changing), on all other platforms current frequency is represented as the nominal “fixed” value.

.. code-block:: python

    >>> import psutil
    >>> psutil.cpu_freq()
    scpufreq(current=931.42925, min=800.0, max=3500.0)
    >>> psutil.cpu_freq(percpu=True)
    [scpufreq(current=2394.945, min=800.0, max=3500.0),
     scpufreq(current=2236.812, min=800.0, max=3500.0),
     scpufreq(current=1703.609, min=800.0, max=3500.0),
     scpufreq(current=1754.289, min=800.0, max=3500.0)]

What CPU a process is on
------------------------

This will let you know what CPU number a process is currently running on, which is somewhat related to the existent `cpu_affinity() <https://pythonhosted.org/psutil/#psutil.Process.cpu_affinity>`__ functionality. The relevant commit is `here <https://github.com/giampaolo/psutil/pull/954/files>`__. It is interesting to use this method to visualize how the OS scheduler continuously evenly reassigns processes to different CPUs  (see `cpu_distribution.py <https://github.com/giampaolo/psutil/blob/master/scripts/cpu_distribution.py>`__ script).


CPU affinity
------------

A new syntax can now be used as an alias for "set affinity against all eligible CPUs".

.. code-block:: python

    Process().cpu_affinity([])

This was implemented because it turns out `on Linux <https://github.com/giampaolo/psutil/issues/956>`__ it is not always possible to set affinity against all CPUs. Having such an alias is also a shortcut to avoid doing this, which is kinda verbose:

.. code-block:: python

    psutil.Process().cpu_affinity(list(range(psutil.cpu_count())))

Other bug fixes
---------------

See `full list <https://github.com/giampaolo/psutil/blob/master/HISTORY.rst#510>`__.
