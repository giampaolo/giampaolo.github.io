Making constants part of your API is evil
#########################################

:date: 2013-12-21
:tags: python, api-design

One of the initial features which were included in `psutil <https://github.com/giampaolo/psutil/>`__ since day one (5 years ago) were system's boot time, number of CPUs and total physical memory. These metrics have one thing in common: they are (apparently) not supposed to change over time. That is why we (me and `Jay <http://www.jayloden.com/>`__) decided that exposing them as module constants calculated at import time was the way to go.

.. code-block:: python

    >>> import psutil
    >>> psutil.NUM_CPUS
    2
    >>> psutil.BOOT_TIME  # as seconds since the epoch
    1387579049.799092
    >>> psutil.TOTAL_PHYMEM
    8374120448

5 years later I regret that decision and I'm going to explain you why you don't want to do the same mistake.

A constant should not change
----------------------------

When we think of  'constants', our expectations are that they should not change over time. It may be obvious, but before thinking about introducing a constant be absolutely sure the value it represents is going to remain the same.
Now, back then we thought these 3 metrics were not supposed to change, at least until the system is rebooted. Well, we were wrong: it turns out 2 of them actually can.
Apparently virtualized systems can change physical installed memory at runtime (see `here <https://code.google.com/p/psutil/issues/detail?id=140#c5>`__ and `here <http://technet.microsoft.com/en-us/library/hh831766.aspx>`__) and system boot time can easily be altered every time you update the system clock.
In both of these cases, of course, the constants will not reflect the updated values.

Doing things at import time is dangerous
----------------------------------------

That's because import time usually means startup time and if something goes wrong the whole application will crash. In general the only reason for a module to crash at import time is because of a missing dependancy or because it's not supposed to run on that platform in the first place.
Now, here's a couple of bug reports which were collected over time: `issue 188 <https://code.google.com/p/psutil/issues/detail?id=188>`__, `issue 313 <https://code.google.com/p/psutil/issues/detail?id=133>`__.
The inconvenience was so severe that I had to release different fixed versions ASAP and the fix consisted of a `stinky workaround <https://code.google.com/p/psutil/source/browse/psutil/_psosx.py?name=release-1.2.1#24>`__.
That's when I started thinking about getting rid of those constants once and for all and introduce functions instead. But how to do that without breaking everybody's code?

Backward compatibility matters
------------------------------

Now here's the crucial part: every time you deliver a library to someone else you just cannot remove an API all of the sudden, especially if they are 3 and have been around since day one.
It should first be deprecated, possibly turned into an alias pointing to a newer API and finally be removed after 1 or 2 major releases. Also, you want the deprecated API to explicitly raise a DeprecationWarning informing the user he's relying on something which will eventually be removed. With a module constant you cannot do any of that. What you would need is a module property.

Module properties
-----------------

One of the greatest things about Python is that it's so dynamic that it lets you do all sort of nasty things with objects, including injecting names into modules (which are also objects) and make them behave like actual class properties!
For this I have to thank `Josiah Carlson <http://www.dr-josiah.com/2013/12/properties-on-python-modules.html>`__ who came up with this very simple yet effective solution:

.. code-block:: python

    class ModuleWrapper(object):

        def __repr__(self):
            return repr(self._module)
        __str__ = __repr__

        @property
        def NUM_CPUS(self):
            msg = "NUM_CPUS constant is deprecated; use cpu_count() instead"
            warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
            return cpu_count()

        @property
        def BOOT_TIME(self):
            msg = "BOOT_TIME constant is deprecated; " \
                  "use get_boot_time() instead"
            warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
            return get_boot_time()

        @property
        def TOTAL_PHYMEM(self):
            msg = "TOTAL_PHYMEM constant is deprecated; " \
                  "use virtual_memory().total instead"
            warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
            return virtual_memory().total

    mod = ModuleWrapper()
    mod.__dict__ = globals()
    mod._module = sys.modules[__name__]
    sys.modules[__name__] = mod

You can put this at the bottom of your module and you'll have fully working module constants (tested on Python from 2.4 to 3.4)!

**EDIT**: the only reason I applied this hack is to turn the old constants into aliases pointing to the newly introduced functions and produce a deprecation warning. That aside I can't think of a case where the use of a module property would be justified.
