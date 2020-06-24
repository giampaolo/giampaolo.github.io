psutil 5.4.0 and AIX support
############################

:date: 2017-10-12
:tags: psutil, aix, python

After a long time `psutil <https://github.com/giampaolo/psutil/>`__ finally adds support for a brand new exotic platform: AIX! Honestly I am not sure how many AIX Python users are out there (I suppose not many) but still, here it is. For this we have to thank Arnon Yaari who started working on the porting a `couple of years ago <https://github.com/giampaolo/psutil/issues/605>`__. To be honest I was skeptical at first because AIX is the only platform which I cannot virtualize and test on my laptop so that made me a bit nervous but Arnon did a very good job. The final `PR <https://github.com/giampaolo/psutil/pull/1123>`__ is huge, it required a considerable amount of work on his part and a review process of over 140 messages which were exchanged between me and him over the course of over 1 month during which I was travelling through China. The final result is very good, basically (almost) all original unit tests pass and the quality of the submitted code is awesome which (I must say) is kind of unusual for an external contribution like this one. Kudos to you Arnon! ;-)

Other than AIX support, release 5.4.0 also includes a couple of important bug fixes for sensors_temperatures() and sensors_fans() functions on Linux and the fix of a bug on OSX which could cause a segmentation fault when using Process.open_files(). Complete list of bugfixes is `here <https://github.com/giampaolo/psutil/blob/master/HISTORY.rst#540>`__.

In terms of future contributions for exotic and still unsupported platforms it is worth mentioning a (still incomplete) PR for `Cygwin <https://github.com/giampaolo/psutil/pull/998>`__ which looks promising and `Mingw32 <https://github.com/giampaolo/psutil/pull/845>`__ compiler support on Windows. It looks like psutil is gradually getting to a point where the addition of new functionalities is becoming more rare, so it is good that support for new platforms happens now when the API is mature and stable. Future development in this direction can also include Android and (hopefully) IOS support. Now *that* would be really awesome to have! =)

Stay tuned.

External links
--------------

* `Reddit <https://www.reddit.com/r/Python/comments/75wsfu/psutil_540_with_aix_support_is_out/>`__
* `HackerNews <http://grodola.blogspot.com/2017/10/psutil-540-with-aix-support-is-out.html>`__


