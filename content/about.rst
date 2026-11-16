About
#####

.. raw:: html

    <div class="about-photo">
        <a href="/images/me-chicago.jpg">
        <img alt="Giampaolo Rodola in Chicago, 2016" src="/images/me-chicago.jpg" style="width:180px; height:180px" />
        </a>
        <br />
    </div>

My name is Giampaolo Rodola. I'm a Python developer who loves writing open source libraries for fun. I'm mostly known for being the author of `psutil`_, which is among the `top 100 <https://psutil.io/adoption/>`__ most downloaded packages on PyPI (400+ million downloads per month, used by 800,000+ GitHub repositories). I've also been a Python core developer since 2010.

Projects
--------

* `psutil`_: a cross-platform library for retrieving information on running processes and system utilization (CPU, memory, disks, network) in Python.  *(2008 - now)*

  .. image:: https://img.shields.io/github/stars/giampaolo/psutil
    :target: https://github.com/giampaolo/psutil/stargazers
    :alt: Github stars

  .. image:: https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fsql-clickhouse.clickhouse.com%2F%3Fuser%3Dplay%26query%3DWITH%2B%2528SELECT%2Bmax%2528date%2529%2BFROM%2Bpypi.pypi_downloads_per_day%2BWHERE%2Bproject%253D%2527psutil%2527%2529%2BAS%2Bm%2BSELECT%2Bconcat%2528toString%2528round%2528sum%2528count%2529%2B%252F%2B1e6%2529%2529%252C%2B%2527M%2527%2529%2BAS%2Bn%2BFROM%2Bpypi.pypi_downloads_per_day%2BWHERE%2Bproject%253D%2527psutil%2527%2BAND%2Bdate%2B%253E%2Bm%2B-%2BtoIntervalMonth%25281%2529%2BAND%2Bdate%2B%253C%253D%2Bm%2BFORMAT%2BJSONEachRow&query=%24.n&label=downloads%2Fmonth&color=blue&cacheSeconds=86400
    :target: https://clickpy.clickhouse.com/dashboard/psutil
    :alt: Downloads

* `pyftpdlib`_: a very fast, asynchronous, pure-Python FTP server.  *(2006 - now)*

  .. image:: https://img.shields.io/github/stars/giampaolo/pyftpdlib
    :target: https://github.com/giampaolo/pyftpdlib/stargazers
    :alt: Github stars

  .. image:: https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fsql-clickhouse.clickhouse.com%2F%3Fuser%3Dplay%26query%3DWITH%2B%2528SELECT%2Bmax%2528date%2529%2BFROM%2Bpypi.pypi_downloads_per_day%2BWHERE%2Bproject%253D%2527pyftpdlib%2527%2529%2BAS%2Bm%2BSELECT%2Bconcat%2528toString%2528round%2528sum%2528count%2529%2B%252F%2B1e6%252C%2B1%2529%2529%252C%2B%2527M%2527%2529%2BAS%2Bn%2BFROM%2Bpypi.pypi_downloads_per_day%2BWHERE%2Bproject%253D%2527pyftpdlib%2527%2BAND%2Bdate%2B%253E%2Bm%2B-%2BtoIntervalMonth%25281%2529%2BAND%2Bdate%2B%253C%253D%2Bm%2BFORMAT%2BJSONEachRow&query=%24.n&label=downloads%2Fmonth&color=blue&cacheSeconds=86400
    :target: https://clickpy.clickhouse.com/dashboard/pyftpdlib
    :alt: Downloads

* `psleak`_: test framework to detect memory and resource leaks in Python C extensions, including leaks which don't show up in ``tracemalloc`` or RSS.  *(2025 - now)*

CPython
-------

`In 2010 <https://mail.python.org/pipermail/python-committers/2010-April/000891.html>`__ I was given commit access to the Python repository. My `contributions </contributions#python-cpython>`__ are mainly focused on the Python standard library. Some I particularly care about are the event-driven `subprocess.Popen.wait()`_, the zero-copy file copy in `shutil`_, `socket.create_server()`_ and `os.sendfile()`_.

Contributions to other projects
-------------------------------

A `list of the pull requests </contributions>`__ I made to other open source projects.

Writing, talks and interviews
-----------------------------

* `2026, From Python 3.3 to today: ending 15 years of subprocess polling </blog/2026/event-driven-process-waiting>`__
* `2025, Detecting memory leaks in C extensions with psutil and psleak </blog/2025/psutil-heap-introspection-apis>`__
* `2019, PyCon China, Shanghai, Efficient I/O with zero-copy syscalls <static/efficient-io-with-zerocopy-syscalls.pdf>`_
* `2017, PyDev of the Week <https://www.blog.pythonlibrary.org/2017/10/09/pydev-of-the-week-giampaolo-rodola/>`_

Abandoned projects
------------------

Most of these are from when I took my first steps with Python in 2005. Listed here mainly for historical / nostalgic reasons.

* `pysendfile`_: a binding to the `sendfile(2)` syscall which lets you send a file twice as fast as with a common socket. *(2011 - deprecated)*
* `soicmp`_: a remote shell using ICMP protocol instead of TCP. *(2005 - 2006)*
* `pypk`_: a port knocker based on `libpcap`. *(2005 - 2006)*
* `pftpd`_: a thread-based FTP server, the ancestor of `pyftpdlib`_. *(2005 - 2006)*
* `ActiveState recipes <https://web.archive.org/web/20251124031558/https://code.activestate.com/recipes/users/4178764/>`__: whatever was not big enough to become an actual project I used to turn into a recipe.

Contacts
--------

* `GitHub <https://github.com/giampaolo>`__
* `X <https://x.com/grodola>`__
* `LinkedIn <https://www.linkedin.com/in/grodola/>`__
* `Medium <https://medium.com/@g.rodola>`__
* Email: `g.rodola@gmail.com <mailto:g.rodola@gmail.com>`__ (`PGP public key
  </static/pgp.txt>`__, `keybase.io <https://keybase.io/grodola>`__)
* PGP fingerprint: ``94B5 05ED EAE6 0CD7 3A1A 56BE 0E22 73E7 308B CC35``

.. _`os.sendfile()`: https://docs.python.org/3/library/os.html#os.sendfile
.. _`psleak`: https://github.com/giampaolo/psleak
.. _`psutil`: https://psutil.io
.. _`pyftpdlib`: https://github.com/giampaolo/pyftpdlib
.. _`pypk`: https://web.archive.org/web/20170313092008/http://billiejoex.altervista.org/Prj_Py_port_knock.htm
.. _`pftpd`: https://web.archive.org/web/20110511030034/http://billiejoex.altervista.org/Prj_pftpd.htm
.. _`pysendfile`: https://github.com/giampaolo/pysendfile
.. _`shutil`: https://docs.python.org/3/library/shutil.html#shutil-platform-dependent-efficient-copy-operations
.. _`subprocess.Popen.wait()`: https://docs.python.org/3/library/subprocess.html#subprocess.Popen.wait
.. _`socket.create_server()`: https://docs.python.org/3/library/socket.html#socket.create_server
.. _`soicmp`: https://soicmp.sourceforge.net/
