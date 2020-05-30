psutil 4.2.0: Windows services in Python
########################################

:date: 2016-05-15
:tags: psutil, windows

New `psutil <https://github.com/giampaolo/psutil>`__ 4.2.0 is out. The main feature of this release is the support for Windows services:

.. code-block:: python

    >>> import psutil
    >>> list(psutil.win_service_iter())
    [<WindowsService(name='AeLookupSvc', display_name='Application Experience') at 38850096>,
     <WindowsService(name='ALG', display_name='Application Layer Gateway Service') at 38850128>,
     <WindowsService(name='APNMCP', display_name='Ask Update Service') at 38850160>,
     <WindowsService(name='AppIDSvc', display_name='Application Identity') at 38850192>,
     ...]
    >>> s = psutil.win_service_get('alg')
    >>> s.as_dict()
    {'binpath': 'C:\\Windows\\System32\\alg.exe',
     'description': 'Provides support for 3rd party protocol plug-ins for Internet Connection Sharing',
     'display_name': 'Application Layer Gateway Service',
     'name': 'alg',
     'pid': None,
     'start_type': 'manual',
     'status': 'stopped',
     'username': 'NT AUTHORITY\\LocalService'}

I did this mainly because I find pywin32 APIs too low level. Having something like this in psutil can be useful to discover and monitor services more easily. The code changes are `here <https://github.com/giampaolo/psutil/pull/803/files>`__ and here's the `doc <https://psutil.readthedocs.io/en/latest/#windows-services>`__. The API for querying a service is similar to ``psutil.Process``. You can get a reference to a service object by using its name (which is unique for every service) and then use name(), status(), etc..:

.. code-block:: python

    >>> s = psutil.win_service_get('alg')
    >>> s.name()
    'alg'
    >>> s.status()
    'stopped'

Initially I thought to expose and provide a complete set of APIs to handle all aspects of service handling including ``start()``, ``stop()``, ``restart()``, ``install()``, uninstall() and modify() but I soon realized that I would have ended up reimplementing what pywin32 already provides at the cost of overcrowding psutil API (see my reasoning `here <https://github.com/giampaolo/psutil/blob/d28de253a2e6d7f368e5260d7a4ab14b285c5083/psutil/_pswindows.py#L426>`__). I think psutil should really be about monitoring, not about installing and modifying system stuff, especially something as critical as a Windows service.

Considerations about Windows services
-------------------------------------

For those of you who are not familiar with Windows, a service is something, generally an executable (.exe), which runs at system startup and keeps running in background. We can say they are the equivalent of a UNIX init script. All service are controlled by a "manager" which keeps track of their status and metadata (e.g. description, startup type) and with that you can start and stop them. It is interesting to note that since (most) services are bound to an executable (and hence a process) you can reference the process via its PID:

.. code-block:: python

    >>> s = psutil.win_service_get('sshd')
    >>> s
    <WindowsService(name='sshd', display_name='Open SSH server') at 38853046>
    >>> s.pid()
    1865
    >>> p = psutil.Process(1865)
    >>> p
    <psutil.Process(pid=19547, name='sshd.exe') at 140461487781328>
    >>> p.exe()
    'C:\CygWin\bin\sshd'

Other improvements
------------------

psutil 4.2.0 comes with 2 other enhancements for Linux:

* psutil.virtual_memory() returns a new "shared" memory field. This is the same value reported by "free" cmdline utility.
* I changed the way how /proc was parsed. Instead of reading /proc/{pid}/status line by line I used a regular expression. Here's the speedups:
   - Process.ppid() is 20% faster
   - Process.status() is 28% faster
   - Process.name() is 25% faster
   - Process.num_threads() is 20% faster (on Python 3 only; on Python 2 it's a bit slower; I suppose re module received some improvements)

External links
--------------

* `Reddit <https://www.reddit.com/r/Python/comments/4jf8tz/psutil_420_windows_services_and_python/>`__
* `Hacker news <https://news.ycombinator.com/item?id=11700002>`__

