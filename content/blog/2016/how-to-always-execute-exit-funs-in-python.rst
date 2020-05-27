How to always execute exit functions in Python
##############################################

:date: 2016-02-12
:tags: python

*...or why atexit.register() and signal.signal() are evil*

* **UPDATE (2016-02-13)**: this recipe no longer handles SIGINT, SIGQUIT and SIGABRT as aliases for "application exit" because it was a bad idea. It only handles SIGTERM. Also it no longer support Windows because signal.signal() implementation is too different than POSIX.*

Many people erroneously think that any function registered via atexit module is guaranteed to always be executed when the program terminates. You may have noticed this is not the case when, for example, you daemonize your app in production then try to stop it or restart it: the cleanup functions will not be executed. This is because functions registered wth atexit module are not called when the program is killed by a signal:

.. code-block:: python

    import atexit, os, signal

    @atexit.register
    def cleanup():
        print("on exit")  # XXX this never gets printed

    os.kill(os.getpid(), signal.SIGTERM)

It must be noted that the same thing would happen if instead of atexit.register() we would use a "finally" clause. It turns out the correct way to make sure the exit function is always called in case a signal is received is to register it via signal.signal(). That has a drawback though: in case a third-party module has already registered a function for that signal (SIGTERM or whatever), your new function will overwrite the old one:

.. code-block:: python

    import os, signal

    def old(*args):
        print("old")  # XXX this never gets printed

    def new(*args):
        print("new")

    signal.signal(signal.SIGTERM, old)
    signal.signal(signal.SIGTERM, new)
    os.kill(os.getpid(), signal.SIGTERM)


Also, we would still have to use atexit.register() so that the function is called also on "clean" interpreter exit and take into account other signals other than SIGTERM which would cause the process to terminate. This recipe attempts to address all these issues so that:

* the exit function is always executed for all exit signals (SIGTERM, SIGINT, SIGQUIT, SIGABRT) on SIGTERM and on "clean" interpreter exit.
* any exit function(s) previously registered via atexit.register() or signal.signal() will be executed as well (after the new one).
* It must be noted that the exit function will never be executed in case of SIGKILL, SIGSTOP or os._exit().

The code
--------

.. code-block:: python

    """
    Function / decorator which tries very hard to register a function to
    be executed at importerer exit.

    Author: Giampaolo Rodola'
    License: MIT
    """

    from __future__ import print_function
    import atexit
    import os
    import functools
    import signal
    import sys


    _registered_exit_funs = set()
    _executed_exit_funs = set()


    def register_exit_fun(fun=None, signals=[signal.SIGTERM],
                          logfun=lambda s: print(s, file=sys.stderr)):
        """Register a function which will be executed on "normal"
        interpreter exit or in case one of the `signals` is received
        by this process (differently from atexit.register()).
        Also, it makes sure to execute any other function which was
        previously registered via signal.signal(). If any, it will be
        executed after our own `fun`.

        Functions which were already registered or executed via this
        function will be ignored.

        Note: there's no way to escape SIGKILL, SIGSTOP or os._exit(0)
        so don't bother trying.

        You can use this either as a function or as a decorator:

            @register_exit_fun
            def cleanup():
                pass

            # ...or

            register_exit_fun(cleanup)

        Note about Windows: I tested this some time ago and didn't work
        exactly the same as on UNIX, then I didn't care about it
        anymore and didn't test since then so may not work on Windows.

        Parameters:

        - fun: a callable
        - signals: a list of signals for which this function will be
          executed (default SIGTERM)
        - logfun: a logging function which is called when a signal is
          received. Default: print to standard error. May be set to
          None if no logging is desired.
        """
        def stringify_sig(signum):
            if sys.version_info < (3, 5):
                smap = dict([(getattr(signal, x), x) for x in dir(signal)
                             if x.startswith('SIG')])
                return smap.get(signum, signum)
            else:
                return signum

        def fun_wrapper():
            if fun not in _executed_exit_funs:
                try:
                    fun()
                finally:
                    _executed_exit_funs.add(fun)

        def signal_wrapper(signum=None, frame=None):
            if signum is not None:
                if logfun is not None:
                    logfun("signal {} received by process with PID {}".format(
                        stringify_sig(signum), os.getpid()))
            fun_wrapper()
            # Only return the original signal this process was hit with
            # in case fun returns with no errors, otherwise process will
            # return with sig 1.
            if signum is not None:
                if signum == signal.SIGINT:
                    raise KeyboardInterrupt
                # XXX - should we do the same for SIGTERM / SystemExit?
                sys.exit(signum)

        def register_fun(fun, signals):
            if not callable(fun):
                raise TypeError("{!r} is not callable".format(fun))
            set([fun])  # raise exc if obj is not hash-able

            signals = set(signals)
            for sig in signals:
                # Register function for this signal and pop() the previously
                # registered one (if any). This can either be a callable,
                # SIG_IGN (ignore signal) or SIG_DFL (perform default action
                # for signal).
                old_handler = signal.signal(sig, signal_wrapper)
                if old_handler not in (signal.SIG_DFL, signal.SIG_IGN):
                    # ...just for extra safety.
                    if not callable(old_handler):
                        continue
                    # This is needed otherwise we'll get a KeyboardInterrupt
                    # strace on interpreter exit, even if the process exited
                    # with sig 0.
                    if (sig == signal.SIGINT and
                            old_handler is signal.default_int_handler):
                        continue
                    # There was a function which was already registered for this
                    # signal. Register it again so it will get executed (after our
                    # new fun).
                    if old_handler not in _registered_exit_funs:
                        atexit.register(old_handler)
                        _registered_exit_funs.add(old_handler)

            # This further registration will be executed in case of clean
            # interpreter exit (no signals received).
            if fun not in _registered_exit_funs or not signals:
                atexit.register(fun_wrapper)
                _registered_exit_funs.add(fun)

        # This piece of machinery handles 3 usage cases. register_exit_fun()
        # used as:
        # - a function
        # - a decorator without parentheses
        # - a decorator with parentheses
        if fun is None:
            @functools.wraps
            def outer(fun):
                return register_fun(fun, signals)
            return outer
        else:
            register_fun(fun, signals)
            return fun

Usage
-----

As a function:

.. code-block:: python

    def cleanup():
        print("cleanup")

    register_exit_fun(cleanup)

As a decorator:

.. code-block:: python

    @register_exit_fun
    def cleanup():
        print("cleanup")

Unit tests
----------

This recipe is hosted on ActiveState and has a full set of unittests. It works with Python 2 and 3.
Notes about Windows
On Windows signals are only partially supported meaning a function which was previously registered via signal.signal() will be executed only on interpreter exit, but not if the process receives a signal. Apparently this is a limitation either of Windows or the signal module (most likely Windows).

Because of how different signal.signal() behaves on Windows, this code is UNIX only: http://bugs.python.org/issue26350
Proposal for stdlib inclusion
The fact that atexit module does not handle signals and that signal.signal() overwrites previously registered handlers is unfortunate. It is also confusing because it is not immediately clear which one you are supposed to use (and it turns out you're supposed to use both). Most of the times you have no idea (or don't care) that you're overwriting another exit function. As a user, I would just want to execute an exit function, no matter what, possibly without messing with whatever a module I've previously imported has done with signal.signal(). To me this suggests there could be space for something like "atexit.register_w_signals".

External discussions

* reddit
* hacker news
