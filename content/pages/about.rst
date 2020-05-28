About
#####

.. raw:: html

    <div style="float:right; padding:10px">
        <a href="/static/me-chicago.jpg">
        <img alt="me at Chicago in 2016" src="/static/me-chicago.jpg" style="width:200px; height:220px" />
        </a>
        <br />
    </div>

My name is Giampaolo Rodola. I'm a passionate Python developer who loves writing open source libraries for fun. I'm mostly known for being the author of `psutil`_. Below is a list of my contribution to the world.

Talks
-----

* `Efficient I/O with zero-copy syscalls <(https://drive.google.com/file/d/1-_oKFyFicTQQiJ-BzNmFo7iCsSkPnbYn>`_ (Pycon China 2019)

Interviews
----------

* `2017 <https://www.blog.pythonlibrary.org/2017/10/09/pydev-of-the-week-giampaolo-rodola/>`_

Open source projects
--------------------

* `psutil`_: a cross-platform library for retrieving information on running processes and system utilization (CPU, memory, disks, network) in Python which works on Linux, Windows, OSX, FreeBSD and Solaris.  (2008 - now)
* `pyftpdlib`_: a very fast, asynchronous, pure-python FTP server.  (2006 - now)
* `pysendfile`_: a binding to sendfile(2) syscall which lets you send a file twice as fast as with a common socket.  (2011 - now)

Contributions to python-dev
---------------------------

Being that Python is an important part of my every day life I'm happy to contribute back every time I get the chance. Starting from year `2010 <https://mail.python.org/pipermail/python-committers/2010-April/000891.html>`_ I've been given commit access against Python code repository. My contributions are mainly focused against the Python standard library. Amongst others:

* `BPO-336761 <https://bugs.python.org/issue33671>`_ efficient zero-copy for shtuil.copy* functions,
* os.sendfile()
* socket.sendfile()
* ftplib's FTPS support
* shutil.disk_usage()
* os.get/setpriority()
* signal constant enums
* Solaris /dev/poll support

I'm the current maintainer of ftplib, smtpd, asyncore and asynchat modules. I'm also occasionally active on the python bug tracker and participate in discussions on python-dev and python-ideas mailing lists, mainly as a lurker.

Python recipes
--------------

Whatever is not big enough to become an actual project I usually turn into an independent recipe.
Here's the ones I like the most:

* Log / directory watcher
* IPv4/IPv6 agnostic server
* socket.sendfile()
* disk usage
* wait for PID
* named constant type
* bytes-to-human corverter
* handle exit context manager

Abandoned projects
------------------

These are from when I started moving my first steps with Python. Listed here mainly for historical / nostalgic reasons. =)

* soicmp: a remote shell using ICMP protocol instead of TCP
* pypk: a port knocker based on libpcap
* pftpd: this is the ancestor of pyftpdlib, a multi thread based FTP server. Back then I still didn't know threads are evil. =)

Like my work?
-------------

All the stuff I work on is MIT licensed meaning you can do whatever you want with it. Except from small occasional donations I've never directly earned money out of my projects. If you think my work is worth your money consider making me a donation via paypal or write me a recommendation on Linkedin. If you're interested in psutil updates you can follow me on Twitter or search for #psutil.

Contacts
--------

* Mail: XXX
* Twitter: XXX
* Linkedin: XXX

.. _`psutil`: https://github.com/giampaolo/psutil
.. _`pyftpdlib`: https://github.com/giampaolo/pyftpdlib
.. _`pysendfile`: https://github.com/giampaolo/pysendfile

