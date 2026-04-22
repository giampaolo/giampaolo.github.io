Fixing Unicode in psutil across Python 2 and 3
##############################################

:date: 2017-09-03
:tags: psutil, python, unicode

This one took a while. Adding proper Unicode support to `psutil <https://github.com/giampaolo/psutil/>`__ was four months of auditing, design decisions, and rewriting nearly every API that returned a string. The full journey is documented in `#1040 <https://github.com/giampaolo/psutil/issues/1040>`__, and what follows is a summary.

This can serve as a case study for any Python library with a C extension that needs to support both Python 2 *and* Python 3, as it will encounter the exact same set of problems.

What was broken
---------------

psutil had different APIs returning a string, many of which misbehaved when it came to unicode. There were three distinctive problems (`#1040 <https://github.com/giampaolo/psutil/issues/1040>`__). Each API could:

* **A**: raise a decoding error for non-ASCII strings (Python 3).
* **B**: return ``unicode`` instead of ``str`` (Python 2).
* **C**: return incorrect / invalid encoded data for non-ASCII strings (both).

`Process.memory_maps() <https://psutil.readthedocs.io/en/latest/#psutil.Process.memory_maps>`__ hit all three on various OSes. `disk_partitions() <https://psutil.readthedocs.io/en/latest/#psutil.disk_partitions>`__ raised decoding errors on every UNIX except Linux. Windows service methods leaked ``unicode`` into Python 2 return values. The C extension had accumulated years of ad-hoc encode/decode decisions, with no single rule covering all of them.

It was a mess.

Filesystem or locale encoding?
------------------------------

First problem was that the C extension was using 2 approaches when it came to decoding and returning a string: `PyUnicode_DecodeFSDefault <https://docs.python.org/3/c-api/unicode.html#c.PyUnicode_DecodeFSDefault>`__ (filesystem encoding) for path-like APIs, and `PyUnicode_DecodeLocale <https://docs.python.org/3/c-api/unicode.html#c.PyUnicode_DecodeLocale>`__ (user locale) for non-path strings like `Process.username() <https://psutil.readthedocs.io/en/latest/#psutil.Process.username>`__.

It appeared clear that I had to use ``PyUnicode_DecodeFSDefault`` for all filesystem-related APIs like `Process.exe() <https://psutil.readthedocs.io/en/latest/#psutil.Process.exe>`__ and `Process.open_files() <https://psutil.readthedocs.io/en/latest/#psutil.Process.open_files>`__.

It was less clear, though, when to use ``PyUnicode_DecodeLocale``.

After some back and forth, I decided to use a single encoding for all APIs: the **filesystem encoding** (``PyUnicode_DecodeFSDefault``). This makes the encoding choice an implementation detail of psutil, not something the user has to care about.

Error handling
--------------

Second question was what to do in case the string cannot be correctly decoded (because invalid, corrupted or whatever).

On Python 3 POSIX the answer was easy: ``'surrogateescape'``, which is also what ``PyUnicode_DecodeFSDefault`` uses by default.

Windows was trickier. CPython's own default error handler on Windows had changed across versions: ``'replace'`` before Python 3.6, ``'surrogatepass'`` from 3.6 on (`PEP 529 <https://www.python.org/dev/peps/pep-0529/>`__). Matching CPython would mean psutil behaving differently depending on which Python ran it. I picked ``'replace'`` unconditionally and kept psutil consistent across versions.

And here come the troubles: Python 2 is different. To correctly handle all kinds of strings on Python 2 we should return ``unicode`` instead of ``str``, but I didn't want to do that, nor have APIs which return two different types depending on the circumstance.

Since unicode support is already broken in Python 2 and its stdlib (see `bpo-18695 <https://bugs.python.org/issue18695>`__), I was happy to always return ``str``, use ``"replace"`` as the error handler, and simply consider unicode support in psutil + Python 2 broken.

Final behavior
--------------

Starting from 5.3.0, psutil behaves consistently across all APIs that return a string. The rules are intentionally simple, even if the underlying implementation is not.

The notes below apply to *any* method returning a string such as ``Process.exe()`` or ``Process.cwd()``, including non-filesystem-related methods such as ``Process.username()``:

* all strings are encoded using the OS filesystem encoding (``PyUnicode_DecodeFSDefault``), which varies depending on the platform you're on (e.g. ``'UTF-8'`` on Linux, ``'mbcs'`` on Windows).
* no API call is supposed to crash with ``UnicodeDecodeError``.
* in case of badly encoded data returned by the OS, the following error handlers are used to replace the bad characters in the string:

  - Python 2: ``"replace"``.
  - Python 3: ``"surrogateescape"`` on POSIX, ``"replace"`` on Windows.

* on Python 2 all APIs return bytes (``str`` type), never ``unicode``.
* on Python 2 you can go back to unicode by doing:

  .. code-block:: python

      >>> unicode(proc.exe(), sys.getdefaultencoding(), errors="replace")

The full journey was implemented in PR `#1052 <https://github.com/giampaolo/psutil/pull/1052>`__, and was part of the `5.3.0 release </blog/2017/psutil-530.html>`__.
