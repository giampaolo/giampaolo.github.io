AIX support
###########

:date: 2017-10-12
:tags: psutil, python, new-platform, community, personal, release
:slug: psutil-540-and-aix-support

After a long wait psutil finally supports a new exotic platform: AIX!

Honestly I'm not sure how many AIX Python users are out there (probably not many), but here it is.

For this we have to thank `Arnon Yaari <https://github.com/wiggin15>`__, who started working on the port a couple of years ago (`#605 <https://github.com/giampaolo/psutil/issues/605>`__). I was skeptical at first, because AIX is the only platform I can't virtualize and test on my laptop, so that made me a bit nervous. Arnon did a great job. The final `PR-1123 <https://github.com/giampaolo/psutil/pull/1123>`__ is huge: it required a considerable amount of work on his part, and a review of more than 140 messages exchanged between us over about a month, during which I was travelling through China.

The end result is very good: almost all original unit tests pass, and code quality is awesome, which (I must say) is fairly unusual for an external contribution like this. Kudos to you, Arnon! ;-)

Other changes
-------------

Besides AIX support, release 5.4.0 also includes a couple of important bug fixes for ``psutil.sensors_temperatures()`` and ``psutil.sensors_fans()`` on Linux, and a fix for a bug on macOS that could cause a segmentation fault when using ``Process.open_files()``. The complete list of bug fixes is in the `changelog <https://psutil.readthedocs.io/latest/changelog.html>`__.

The future
----------

Looking ahead at other exotic, still-unsupported platforms, two contributions are worth mentioning: a (still incomplete) PR for Cygwin which looks promising (`PR-998 <https://github.com/giampaolo/psutil/pull/998>`__), and Mingw32 compiler support on Windows (`PR-845 <https://github.com/giampaolo/psutil/pull/845>`__).

psutil is gradually reaching a point where adding new features is becoming rarer, so it's a good moment to welcome new platforms while the API is mature and stable.

Future work along these lines could also include Android and (hopefully) iOS support. Now *that* would be really awesome to have.

Stay tuned.

Discussion
----------

* `Reddit <https://www.reddit.com/r/Python/comments/75wsfu/psutil_540_with_aix_support_is_out/>`__
* `Blogspot <http://grodola.blogspot.com/2017/10/psutil-540-with-aix-support-is-out.html>`__
