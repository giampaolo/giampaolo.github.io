About
#####

.. raw:: html

    <div style="float:right; padding:10px">
        <a href="/images/me-chicago.jpg">
        <img alt="me at Chicago in 2016" src="/images/me-chicago.jpg" style="width:220px; height:220px" />
        </a>
        <br />
    </div>

My name is Giampaolo Rodola. I'm a passionate Python developer who loves writing open source libraries for fun. I'm mostly known for being the author of `psutil`_. I am also a senior consultant and freelancer. Below is a list of my contribution to the world.

Talks
-----

* `2019, Pycon China, Shanghai, Efficient I/O with zero-copy syscalls <static/efficient-io-with-zerocopy-syscalls.pdf>`_

Interviews
----------

* `2017, Pydev of the week <https://www.blog.pythonlibrary.org/2017/10/09/pydev-of-the-week-giampaolo-rodola/>`_

Projects
--------

* `psutil`_: a cross-platform library for retrieving information on running processes and system utilization (CPU, memory, disks, network) in Python which works on Linux, Windows, OSX, FreeBSD and Solaris.  (2008 - now)
* `pyftpdlib`_: a very fast, asynchronous, pure-python FTP server.  (2006 - now)
* `pysendfile`_: a binding to sendfile(2) syscall which lets you send a file twice as fast as with a common socket.  (2011 - now)

python-dev contributions
------------------------

Being that Python is an important part of my every day life I'm happy to contribute back every time I get the chance. Starting from year `2010 <https://mail.python.org/pipermail/python-committers/2010-April/000891.html>`_ I've been given commit access against Python code repository. My contributions are mainly focused against the Python standard library. Amongst others:

+----------+--------------------------+-----------------------------------------------------------+
| BPO      | Module / API             | Description                                               |
+==========+==========================+===========================================================+
| `33671`_ | `shutil`_                | faster file copy with zero-copy syscalls                  |
|          |                          | (`pycon china talk`_)                                     |
+----------+--------------------------+-----------------------------------------------------------+
| `33695`_ | `shutil`_                | faster file copy by using os.scandir + caching            |
+----------+--------------------------+-----------------------------------------------------------+
| `4080`_  | `unittest`_              | unittest timings                                          |
+----------+--------------------------+-----------------------------------------------------------+
| `10882`_ | `os.sendfile`_           | expose sendfile() syscall                                 |
+----------+--------------------------+-----------------------------------------------------------+
| `17552`_ | `socket.sendfile`_       | sendfile() high-level wrapper                             |
+----------+--------------------------+-----------------------------------------------------------+
| `17561`_ | `socket.create_server`_  | utility function for dual-stack IPv4/6 TCP servers        |
+----------+--------------------------+-----------------------------------------------------------+
| `2054`_  | `ftplib.TLS_FTP`_        | FTP over SSL support                                      |
+----------+--------------------------+-----------------------------------------------------------+
| `12442`_ | `shutil.disk_usage`_     | disk usage "df" style                                     |
+----------+--------------------------+-----------------------------------------------------------+
| `10784`_ | `os.getpriority`_,       | get/set process priority                                  |
|          | `os.setpriority`_        |                                                           |
+----------+--------------------------+-----------------------------------------------------------+
| `21076`_ | `signal`_                | signal module constant enums                              |
+----------+--------------------------+-----------------------------------------------------------+
| `18931`_ | `selectors`_             | Solaris /dev/poll support                                 |
+----------+--------------------------+-----------------------------------------------------------+


Python recipes
--------------

Whatever is not big enough to become an actual project I usually turn into an independent recipe.
Here's the ones I like the most:

* `Log / directory watcher <http://code.activestate.com/recipes/577968-log-watcher-tail-f-log/?in=user-4178764>`__
* `IPv4/v6 agnostic server <http://code.activestate.com/recipes/578504-server-supporting-ipv4-and-ipv6/?in=user-4178764>`__
* `socket.sendfile() <https://code.activestate.com/recipes/578889-socketsendfile/>`__ (backport of `BPO-17552 <https://bugs.python.org/issue17552>`__)
* `disk usage <http://code.activestate.com/recipes/577972-disk-usage/?in=user-4178764>`__ (backport of `BPO-12442 <http://bugs.python.org/issue12442>`__)
* `wait for PID <http://code.activestate.com/recipes/578022-wait-for-pid-and-check-for-pid-existance-posix/?in=user-4178764>`__
* `bytes-to-human corverter <http://code.activestate.com/recipes/578019-bytes-to-human-human-to-bytes-converter/?in=user-4178764>`__
* `handle exit context manager <blog/2016/how-to-always-execute-exit-functions-in-python/>`__

Abandoned projects
------------------

These are from when I started moving my first steps with Python in 2005. Listed here mainly for historical / nostalgic reasons. =)

* `soicmp`_: a remote shell using ICMP protocol instead of TCP
* `pypk`_: a port knocker based on libpcap
* pftpd: this is the ancestor of `pyftpdlib`_ (web site is lost), a thread-based FTP server.

Contacts
--------

* Email: `g.rodola@gmail.com <g.rodola@gmail.com>`__
* `GitHub <http://github.com/giampaolo>`__
* `Twitter <https://twitter.com/grodola>`__
* `Linkedin <https://www.linkedin.com/in/grodola/>`__

.. _`psutil`: https://github.com/giampaolo/psutil
.. _`pyftpdlib`: https://github.com/giampaolo/pyftpdlib
.. _`pysendfile`: https://github.com/giampaolo/pysendfile
.. _`33671`: https://bugs.python.org/issue33671
.. _`10882`: https://bugs.python.org/issue10882
.. _`17552`: https://bugs.python.org/issue17552
.. _`2054`: https://bugs.python.org/issue2054
.. _`10784`: https://bugs.python.org/issue10784
.. _`21076`: https://bugs.python.org/issue21076
.. _`18931`: https://bugs.python.org/issue18931
.. _`12442`: http://bugs.python.org/issue12442
.. _`4080`: https://bugs.python.org/issue4080
.. _`17561`: https://bugs.python.org/issue17561
.. _`33695`: https://bugs.python.org/issue33695
.. _`pycon china talk`: static/efficient-io-with-zerocopy-syscalls.pdf
.. _`shutil`: https://docs.python.org/3/library/shutil.html#shutil-platform-dependent-efficient-copy-operations
.. _`os.sendfile`: https://docs.python.org/3/library/os.html#os.sendfile
.. _`socket.sendfile`: https://docs.python.org/3/library/socket.html#socket.socket.sendfile
.. _`ftplib.TLS_FTP`: https://docs.python.org/3/library/ftplib.html#ftplib.FTP_TLS
.. _`os.getpriority`: https://docs.python.org/3/library/os.html#os.getpriority
.. _`os.setpriority`: https://docs.python.org/3/library/os.html#os.setpriority
.. _`signal`: https://docs.python.org/3/library/signal.html
.. _`unittest`: https://docs.python.org/3/library/unittest.html
.. _`selectors`: https://docs.python.org/3/library/selectors.html
.. _`soicmp`: http://soicmp.sourceforge.net/
.. _`pypk`: https://sourceforge.net/projects/pypk/
.. _`shutil.disk_usage`: https://docs.python.org/3/library/shutil.html?highlight=ftplib#shutil.disk_usage
.. _`socket.create_server`: https://docs.python.org/3/library/socket.html#socket.create_server
