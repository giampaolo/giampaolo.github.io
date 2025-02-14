Title: psutil: drop Python 2.7 support
Date: 2025-02-13
Tags: psutil, python
Authors: Giampaolo Rodola

About dropping Python 2.7 support, 3 years ago [I stated](https://github.com/giampaolo/psutil/issues/2014#issuecomment-969263432):

> Not a chance, for many years to come. [Python 2.7] currently represents 7-10%
> of total downloads, meaning around 70k / 100k downloads per day.

Only 3 years later, and to my surprise, **downloads for Python 2.7 dropped to
0.36%**! As such, as of psutil 7.0.0, I finally decided to drop support for
Python 2.7!

## The numbers

These are downloads per month:

```
$ pypinfo --percent psutil pyversion
Served from cache: False
Data processed: 4.65 GiB
Data billed: 4.65 GiB
Estimated cost: $0.03

| python_version | percent | download_count |
| -------------- | ------- | -------------- |
| 3.10           |  23.84% |     26,354,506 |
| 3.8            |  18.87% |     20,862,015 |
| 3.7            |  17.38% |     19,217,960 |
| 3.9            |  17.00% |     18,798,843 |
| 3.11           |  13.63% |     15,066,706 |
| 3.12           |   7.01% |      7,754,751 |
| 3.13           |   1.15% |      1,267,008 |
| 3.6            |   0.73% |        803,189 |
| 2.7            |   0.36% |        402,111 |
| 3.5            |   0.03% |         28,656 |
| Total          |         |    110,555,745 |
```

According to [pypistats.org](https://archive.is/wip/knzql) Python 2.7 downloads
are 0.28% of the total, around 15.000 downloads per day.

## The pain

Maintaining 2.7 support in psutil had become increasingly difficult, but still
possible. E.g. I could still run tests by using [old PYPI
backports](https://github.com/giampaolo/psutil/blob/fbb6d9ce98f930d3d101b7df5a4f4d0f1d2b35a3/setup.py#L76-L85).
GitHub Actions could still be
[tweaked](https://github.com/giampaolo/psutil/blob/fbb6d9ce98f930d3d101b7df5a4f4d0f1d2b35a3/.github/workflows/build.yml#L77-L112)
to run tests and produce wheels on Linux and macOS. Not on Windows though, for
which we have to use a separate service (Appveyor).
Still, the amount of hacks in psutil source code necessary to support Python
2.7 piled up over the years, and became quite big. Some disadvantages that come
to mind:

* Having to maintain a Python compatibility layers like
  [psutil/_compat.py](https://github.com/giampaolo/psutil/blob/fbb6d9ce98f930d3d101b7df5a4f4d0f1d2b35a3/psutil/_compat.py).
  This translated in extra extra code and extra imports.
* The C compatibility layer to differentiate between Python 2 and 3 (`#if
  PY_MAJOR_VERSION <= 3`, etc.).
* Dealing with the string vs. unicode differences, both in Python and in C.
* Inability to use modern language features, especially f-strings.
* Inability to freely use `enum`s, which created a difference on how CONSTANTS
  were exposed in terms of API.
* Having to install a specific version of `pip` and other (outdated)
  [deps](https://github.com/giampaolo/psutil/blob/fbb6d9ce98f930d3d101b7df5a4f4d0f1d2b35a3/setup.py#L76-L85).
* Relying on the third-party Appveyor CI service to run tests and produce 2.7
  wheels.
* Running 4 extra CI jobs on every commit (Linux, macOS, Windows 32-bit,
  Windows 64-bit) making the CI slower and more subject to failures (we have
  quite a bit of flaky tests).
* The distribution of 7 wheels specific for Python 2.7. E.g. in the previous
  release I had to upload:

```
psutil-6.1.1-cp27-cp27m-macosx_10_9_x86_64.whl
psutil-6.1.1-cp27-none-win32.whl
psutil-6.1.1-cp27-none-win_amd64.whl
psutil-6.1.1-cp27-cp27m-manylinux2010_i686.whl
psutil-6.1.1-cp27-cp27m-manylinux2010_x86_64.whl
psutil-6.1.1-cp27-cp27mu-manylinux2010_i686.whl
psutil-6.1.1-cp27-cp27mu-manylinux2010_x86_64.whl
```

## The removal

The removal was done in
[PR-2841](https://github.com/giampaolo/psutil/pull/2481), which removed around
1500 lines of code (nice!). **It felt liberating**. In doing so, in the doc I
still made the promise that the 6.1.\* serie will keep supporting Python 2.7
and will receive **critical bug-fixes only** (no new features). It will be
maintained in a specific [python2
branch](https://github.com/giampaolo/psutil/tree/python2). I explicitly kept
the
[setup.py](https://github.com/giampaolo/psutil/blob/fbb6d9ce98f930d3d101b7df5a4f4d0f1d2b35a3/setup.py)
script compatible with Python 2.7 in terms of syntax, so that it can emit an
informative error message on pip install. The user trying to install psutil on
Python 2.7 will see:

```
$ pip2 install psutil
As of version 7.0.0 psutil no longer supports Python 2.7.
Latest version supporting Python 2.7 is psutil 6.1.X.
Install it with: "pip2 install psutil==6.1.*".
```

## Related tickets

* 2017-06: [#1053](https://github.com/giampaolo/psutil/issues/1053)
* 2022-04: [#2099](https://github.com/giampaolo/psutil/pull/2099)
* 2023-04: [#2246](https://github.com/giampaolo/psutil/pull/2246)
* 2024-12: [#635](https://github.com/giampaolo/pyftpdlib/pull/635)
