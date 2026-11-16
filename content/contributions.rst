Contributions
#############

Patches and pull requests I contributed to other people's projects over the years. For my own work see the `About </about>`_ page.

`python/cpython <https://github.com/python/cpython>`__
------------------------------------------------------

* 2026-01-19 `gh-83069 <https://github.com/python/cpython/pull/144047>`__: ``subprocess``: use efficient event-driven ``Popen.wait()`` on Linux / macOS / BSD
* 2019-03-11 `bpo-4080 <https://github.com/python/cpython/pull/12271>`__: ``unittest``: add ``--durations`` option to show slowest tests
* 2019-02-07 `bpo-35934 <https://github.com/python/cpython/pull/11784>`__: add ``socket.create_server()``
* 2018-06-23 `bpo-33695 <https://github.com/python/cpython/pull/7874>`__: ``shutil.copytree()``: speedup by using ``os.scandir()`` cache
* 2018-05-28 `bpo-33671 <https://github.com/python/cpython/pull/7160>`__: ``shutil``: efficient zero-copy file copy (Linux, macOS, Windows)
* 2017-04-07 `bpo-30014 <https://github.com/python/cpython/pull/1030>`__: ``selectors``: make ``modify()`` faster for poll-like selectors
* 2014-06-11 `bpo-17552 <https://bugs.python.org/issue17552>`__: add ``socket.sendfile()``
* 2014-04-04 `bpo-21076 <https://bugs.python.org/issue21076>`__: turn ``signal`` module constants into enums
* 2014-03-20 `bpo-18931 <https://bugs.python.org/issue18931>`__: ``selectors``: support ``/dev/poll`` on Solaris
* 2013-04-10 `bpo-17675 <https://bugs.python.org/issue17675>`__: make socket ``repr()`` show local and remote addresses
* 2012-12-31 `bpo-10527 <https://bugs.python.org/issue10527>`__: ``multiprocessing``: use ``poll()`` instead of ``select()`` if available
* 2011-12-14 `bpo-13449 <https://bugs.python.org/issue13449>`__: ``sched``: add ``blocking`` parameter to ``scheduler.run()``
* 2011-12-14 `bpo-8684 <https://bugs.python.org/issue8684>`__: ``sched``: make ``scheduler`` class thread-safe
* 2011-07-01 `bpo-12442 <https://bugs.python.org/issue12442>`__: add ``shutil.disk_usage()``
* 2011-05-06 `bpo-11072 <https://bugs.python.org/issue11072>`__: ``ftplib``: add MLSD command support (RFC 3659)
* 2011-02-25 `bpo-10882 <https://bugs.python.org/issue10882>`__: add ``os.sendfile()``
* 2011-02-25 `bpo-10784 <https://bugs.python.org/issue10784>`__: add ``os.getpriority()`` and ``os.setpriority()``
* 2010-10-04 `bpo-6706 <https://bugs.python.org/issue6706>`__: ``asyncore``: add ``handle_accepted()`` method
* 2010-09-08 `bpo-9794 <https://bugs.python.org/issue9794>`__: add context manager protocol to ``socket.socket``
* 2010-05-26 `bpo-8806 <https://bugs.python.org/issue8806>`__: ``ftplib``: add SSL contexts support
* 2010-05-10 `bpo-4972 <https://bugs.python.org/issue4972>`__: ``ftplib``: add context manager protocol to ``FTP`` class
* 2009-11-15 `bpo-2054 <https://bugs.python.org/issue2054>`__: ``ftplib``: add ``FTP_TLS`` class (FTP over TLS)
* Minor: `#143515 <https://github.com/python/cpython/pull/143515>`__, `#103209 <https://github.com/python/cpython/pull/103209>`__, `#26024 <https://github.com/python/cpython/pull/26024>`__, `#18261 <https://github.com/python/cpython/pull/18261>`__, `#17552 <https://github.com/python/cpython/pull/17552>`__, `#17313 <https://github.com/python/cpython/pull/17313>`__, `#16491 <https://github.com/python/cpython/pull/16491>`__, `#13676 <https://github.com/python/cpython/pull/13676>`__, `#13675 <https://github.com/python/cpython/pull/13675>`__, `#12735 <https://github.com/python/cpython/pull/12735>`__, `#12183 <https://github.com/python/cpython/pull/12183>`__, `#12016 <https://github.com/python/cpython/pull/12016>`__, `#11997 <https://github.com/python/cpython/pull/11997>`__, `#11772 <https://github.com/python/cpython/pull/11772>`__, `#11686 <https://github.com/python/cpython/pull/11686>`__, `#7681 <https://github.com/python/cpython/pull/7681>`__, `#2108 <https://github.com/python/cpython/pull/2108>`__, `#2082 <https://github.com/python/cpython/pull/2082>`__, `#1534 <https://github.com/python/cpython/pull/1534>`__, `#1331 <https://github.com/python/cpython/pull/1331>`__, `#1035 <https://github.com/python/cpython/pull/1035>`__, `bpo-6916 <https://bugs.python.org/issue6916>`__, `bpo-13248 <https://bugs.python.org/issue13248>`__, `bpo-16038 <https://bugs.python.org/issue16038>`__, `bpo-17996 <https://bugs.python.org/issue17996>`__, `bpo-17992 <https://bugs.python.org/issue17992>`__, `bpo-17707 <https://bugs.python.org/issue17707>`__, `bpo-17452 <https://bugs.python.org/issue17452>`__, `bpo-17197 <https://bugs.python.org/issue17197>`__, `bpo-16646 <https://bugs.python.org/issue16646>`__, `bpo-16270 <https://bugs.python.org/issue16270>`__, `bpo-16264 <https://bugs.python.org/issue16264>`__, `bpo-14807 <https://bugs.python.org/issue14807>`__, `bpo-14800 <https://bugs.python.org/issue14800>`__, `bpo-10340 <https://bugs.python.org/issue10340>`__, `bpo-13694 <https://bugs.python.org/issue13694>`__, `bpo-13563 <https://bugs.python.org/issue13563>`__, `bpo-11049 <https://bugs.python.org/issue11049>`__, `bpo-12139 <https://bugs.python.org/issue12139>`__, `bpo-12002 <https://bugs.python.org/issue12002>`__, `bpo-11289 <https://bugs.python.org/issue11289>`__, `bpo-11351 <https://bugs.python.org/issue11351>`__, `bpo-11265 <https://bugs.python.org/issue11265>`__, `bpo-9795 <https://bugs.python.org/issue9795>`__, `bpo-11348 <https://bugs.python.org/issue11348>`__, `bpo-8594 <https://bugs.python.org/issue8594>`__, `bpo-11323 <https://bugs.python.org/issue11323>`__, `bpo-11291 <https://bugs.python.org/issue11291>`__, `bpo-11232 <https://bugs.python.org/issue11232>`__, `bpo-11214 <https://bugs.python.org/issue11214>`__, `bpo-11177 <https://bugs.python.org/issue11177>`__, `bpo-9693 <https://bugs.python.org/issue9693>`__, `bpo-9711 <https://bugs.python.org/issue9711>`__, `bpo-9706 <https://bugs.python.org/issue9706>`__, `bpo-9601 <https://bugs.python.org/issue9601>`__, `bpo-9129 <https://bugs.python.org/issue9129>`__, `bpo-8866 <https://bugs.python.org/issue8866>`__, `bpo-8807 <https://bugs.python.org/issue8807>`__, `bpo-8857 <https://bugs.python.org/issue8857>`__, `bpo-8687 <https://bugs.python.org/issue8687>`__, `bpo-6822 <https://bugs.python.org/issue6822>`__, `bpo-2944 <https://bugs.python.org/issue2944>`__, `bpo-6589 <https://bugs.python.org/issue6589>`__, `bpo-8573 <https://bugs.python.org/issue8573>`__, `bpo-8490 <https://bugs.python.org/issue8490>`__, `bpo-8543 <https://bugs.python.org/issue8543>`__, `bpo-4841 <https://bugs.python.org/issue4841>`__, `bpo-3817 <https://bugs.python.org/issue3817>`__, `bpo-4088 <https://bugs.python.org/issue4088>`__, `bpo-3939 <https://bugs.python.org/issue3939>`__, `bpo-2055 <https://bugs.python.org/issue2055>`__, `bpo-1960 <https://bugs.python.org/issue1960>`__, `bpo-2026 <https://bugs.python.org/issue2026>`__, `bpo-1959 <https://bugs.python.org/issue1959>`__, `bpo-1938 <https://bugs.python.org/issue1938>`__

`felix-hilden/sphinx-codeautolink <https://github.com/felix-hilden/sphinx-codeautolink>`__
------------------------------------------------------------------------------------------

* 2026-11-04 `#205 <https://github.com/felix-hilden/sphinx-codeautolink/pull/205>`__: Inject links at write time instead of rewriting HTML files after the build
* 2026-04-24 `#197 <https://github.com/felix-hilden/sphinx-codeautolink/pull/197>`__: Resolve return annotations that use ``TYPE_CHECKING``
* 2026-04-24 `#196 <https://github.com/felix-hilden/sphinx-codeautolink/pull/196>`__: Resolve for-loop targets coming from calls returning a hinted iterable
* Minor: `#204 <https://github.com/felix-hilden/sphinx-codeautolink/pull/204>`__, `#199 <https://github.com/felix-hilden/sphinx-codeautolink/pull/199>`__

`sphinx-doc/sphinx <https://github.com/sphinx-doc/sphinx>`__
------------------------------------------------------------

* 2026-11-04 `#14816 <https://github.com/sphinx-doc/sphinx/pull/14816>`__: Raise the GC threshold in sphinx-build *(open)*
* Minor: `#14814 <https://github.com/sphinx-doc/sphinx/pull/14814>`__ *(open)*, `#14801 <https://github.com/sphinx-doc/sphinx/pull/14801>`__ *(open)*

`pytest-dev/pytest <https://github.com/pytest-dev/pytest>`__
------------------------------------------------------------

* 2026-08-13 `#14874 <https://github.com/pytest-dev/pytest/pull/14874>`__: Defer pygments and pdb imports (9% speedup) *(not merged)*

`numpy/numpy <https://github.com/numpy/numpy>`__
------------------------------------------------

* 2026-01-05 `#30583 <https://github.com/numpy/numpy/pull/30583>`__: ENH: add C memory leak regression tests *(not merged)*

`pytest-dev/pytest-subtests <https://github.com/pytest-dev/pytest-subtests>`__
------------------------------------------------------------------------------

* 2025-06-25 `#199 <https://github.com/pytest-dev/pytest-subtests/pull/199>`__: Add ``--no-subtest-reports`` CLI opt

`PyCQA/autoflake <https://github.com/PyCQA/autoflake>`__
--------------------------------------------------------

* 2022-04-10 `#107 <https://github.com/PyCQA/autoflake/pull/107>`__: Add support for parallel execution (autopep8's ``--jobs`` opt)

`btimby/fulltext <https://github.com/btimby/fulltext>`__
--------------------------------------------------------

* 2017-12-19 `#62 <https://github.com/btimby/fulltext/pull/62>`__: Windows support + AppVeyor CI
* 2017-12-08 `#52 <https://github.com/btimby/fulltext/pull/52>`__: Implement title extraction
* 2017-12-07 `#49 <https://github.com/btimby/fulltext/pull/49>`__: Encapsulate backends logic into a class
* 2017-12-04 `#46 <https://github.com/btimby/fulltext/pull/46>`__: Add unicode support (py 2 and 3)
* Minor: `#90 <https://github.com/btimby/fulltext/pull/90>`__ *(open)*, `#87 <https://github.com/btimby/fulltext/pull/87>`__ *(open)*, `#86 <https://github.com/btimby/fulltext/pull/86>`__ *(open)*, `#85 <https://github.com/btimby/fulltext/pull/85>`__, `#81 <https://github.com/btimby/fulltext/pull/81>`__, `#80 <https://github.com/btimby/fulltext/pull/80>`__, `#78 <https://github.com/btimby/fulltext/pull/78>`__, `#76 <https://github.com/btimby/fulltext/pull/76>`__, `#73 <https://github.com/btimby/fulltext/pull/73>`__, `#71 <https://github.com/btimby/fulltext/pull/71>`__, `#70 <https://github.com/btimby/fulltext/pull/70>`__, `#69 <https://github.com/btimby/fulltext/pull/69>`__, `#60 <https://github.com/btimby/fulltext/pull/60>`__, `#57 <https://github.com/btimby/fulltext/pull/57>`__, `#48 <https://github.com/btimby/fulltext/pull/48>`__, `#47 <https://github.com/btimby/fulltext/pull/47>`__, `#41 <https://github.com/btimby/fulltext/pull/41>`__, `#36 <https://github.com/btimby/fulltext/pull/36>`__, `#34 <https://github.com/btimby/fulltext/pull/34>`__, `#30 <https://github.com/btimby/fulltext/pull/30>`__, `#28 <https://github.com/btimby/fulltext/pull/28>`__, `#27 <https://github.com/btimby/fulltext/pull/27>`__, `#25 <https://github.com/btimby/fulltext/pull/25>`__, `#23 <https://github.com/btimby/fulltext/pull/23>`__, `#20 <https://github.com/btimby/fulltext/pull/20>`__

`btimby/reloadconf <https://github.com/btimby/reloadconf>`__
------------------------------------------------------------

* 2018-02-13 `#9 <https://github.com/btimby/reloadconf/pull/9>`__: Wait / sync  primitives
* Minor: `#11 <https://github.com/btimby/reloadconf/pull/11>`__ *(open)*

`tornadoweb/tornado <https://github.com/tornadoweb/tornado>`__
--------------------------------------------------------------

* 2011-07-05 `#295 <https://github.com/tornadoweb/tornado/pull/295>`__: HTTP server support for UNIX sockets *(not merged)*
