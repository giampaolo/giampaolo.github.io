Title: Speedup pytest startup
Date: 2025-04-04
Tags: psutil, python, pytest, performance
Authors: Giampaolo Rodola

# Preface: the migration to pytest

Last year, after 17 years since the inception of the project, I decided to
start adopting pytest into psutil (see
[psutil/#2446](https://github.com/giampaolo/psutil/issues/2446)). The
advantages over unittest are numerous, but the two I cared about most are:

* Being able to use base `assert` statements instead of unittest's
  `self.assert*()` APIs.
* The excellent [pytest-xdist](https://pypi.org/project/pytest-xdist/)
  extension, that lets you run tests in parallel, basically for free.

Beyond that, I don't rely on any pytest-specific features in the code, like
[fixtures](https://docs.pytest.org/en/6.2.x/fixture.html) or conftest.py. I
still organize tests in classes, with each one inheriting from
`unittest.TestCase`. Why?

* I like unittest's `self.addCleanup` too much to give it up (see some
  [usages](https://github.com/giampaolo/psutil/blob/265fcf94a5da4260beb514653a2124915bf2a4f2/psutil/tests/__init__.py#L984-L1010)).
  I find it superior to fixtures. Less magical and more explicit.
* I want users to be able to test their psutil installation in production
  environments where pytest might not be installed. To accommodate this, I
  created a minimal "fake" pytest class that emulates essential features like
  `pytest.raises`, `@pytest.skip` etc. (see
  [PR-2456](https://github.com/giampaolo/psutil/pull/2456)).

But that's a separate topic. What I want to focus on here is one of pytest's
most frustrating aspects: slow startup times.

# pytest invocation is slow

To measure pytest's startup time, let's run a very [simple
test](https://github.com/giampaolo/psutil/blob/265fcf94a5da4260beb514653a2124915bf2a4f2/psutil/tests/test_misc.py#L232-L236)
where execution time won't significantly affect the results:

```text
$ time python3 -m pytest --no-header psutil/tests/test_misc.py::TestMisc::test_version
============================= test session starts =============================
collected 1 item
psutil/tests/test_misc.py::TestMisc::test_version PASSED
============================== 1 passed in 0.05s ==============================

real    0m0,427s
user    0m0,375s
sys     0m0,051s
```

0,427s. Almost half of a second. That's excessive for something I frequently
execute during development. For comparison, running the same test with
`unittest`:

```text
$ time python3 -m unittest psutil.tests.test_misc.TestMisc.test_version
----------------------------------------------------------------------
Ran 1 test in 0.000s
OK

real    0m0,204s
user    0m0,169s
sys     0m0,035s
```

0,204 secs. Meaning unittest is roughly twice as fast as pytest. But why?

# Where is time being spent?

A significant portion of pytest's overhead comes from import time:

```text
$ time python3 -c "import pytest"
real    0m0,151s
user    0m0,135s
sys     0m0,016s

$ time python3 -c "import unittest"
real    0m0,065s
user    0m0,055s
sys     0m0,010s
```

There's nothing I can do about that. For the record, psutil import timing is:

```text
$ time python3 -c "import psutil"
real    0m0,056s
user    0m0,050s
sys     0m0,006s
```

# Disable plugin auto loading

After some research, I discovered that pytest automatically loads all plugins
installed on the system, even if they aren't used. Here's how to list them
(output is cut):

```text
$ pytest --trace-config --collect-only
...
active plugins:
    ...
    setupplan           : ~/.local/lib/python3.12/site-packages/_pytest/setupplan.py
    stepwise            : ~/.local/lib/python3.12/site-packages/_pytest/stepwise.py
    warnings            : ~/.local/lib/python3.12/site-packages/_pytest/warnings.py
    logging             : ~/.local/lib/python3.12/site-packages/_pytest/logging.py
    reports             : ~/.local/lib/python3.12/site-packages/_pytest/reports.py
    python_path         : ~/.local/lib/python3.12/site-packages/_pytest/python_path.py
    unraisableexception : ~/.local/lib/python3.12/site-packages/_pytest/unraisableexception.py
    threadexception     : ~/.local/lib/python3.12/site-packages/_pytest/threadexception.py
    faulthandler        : ~/.local/lib/python3.12/site-packages/_pytest/faulthandler.py
    instafail           : ~/.local/lib/python3.12/site-packages/pytest_instafail.py
    anyio               : ~/.local/lib/python3.12/site-packages/anyio/pytest_plugin.py
    pytest_cov          : ~/.local/lib/python3.12/site-packages/pytest_cov/plugin.py
    subtests            : ~/.local/lib/python3.12/site-packages/pytest_subtests/plugin.py
    xdist               : ~/.local/lib/python3.12/site-packages/xdist/plugin.py
    xdist.looponfail    : ~/.local/lib/python3.12/site-packages/xdist/looponfail.py
    ...
```

It turns out `PYTEST_DISABLE_PLUGIN_AUTOLOAD` environment variable can be used
to disable them. By running `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest
--trace-config --collect-only` again I can see that the following plugins
disappeared:

```text
anyio
pytest_cov
pytest_instafail
pytest_subtests
xdist
xdist.looponfail
```

Now let's run the test again by using `PYTEST_DISABLE_PLUGIN_AUTOLOAD`:

```text
$ time PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest --no-header psutil/tests/test_misc.py::TestMisc::test_version
============================= test session starts =============================
collected 1 item
psutil/tests/test_misc.py::TestMisc::test_version PASSED
============================== 1 passed in 0.05s ==============================

real    0m0,285s
user    0m0,267s
sys     0m0,040s
```

We went from 0,427 secs to 0,285 secs, a ~40% improvement. Not bad. We now need
to selectively enable only the plugins we actually use, via `-p` CLI option.
Plugins used by psutil are `pytest-instafail` and `pytest-subtests` (we'll
think about `pytest-xdist` later):

```text
$ time PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -p instafail -p subtests --no-header psutil/tests/test_misc.py::TestMisc::test_version
========================================================= test session starts =========================================================
collected 1 item
psutil/tests/test_misc.py::TestMisc::test_version PASSED
========================================================== 1 passed in 0.05s ==========================================================
real    0m0,320s
user    0m0,283s
sys     0m0,037s
```

Time went up again, from 0,285 secs to 0,320s. Quite a slowdown, but still
better than the initial 0,427s. Now, let's add `pytest-xdist` to the mix:

```text
$ time PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -p instafail -p subtests -p xdist --no-header psutil/tests/test_misc.py::TestMisc::test_version
========================================================= test session starts =========================================================
collected 1 item
psutil/tests/test_misc.py::TestMisc::test_version PASSED
========================================================== 1 passed in 0.05s ==========================================================

real    0m0,369s
user    0m0,286s
sys     0m0,049s
```

We now went from 0,320s to 0,369s. Not too much, but still it's a pity to pay
the price when NOT running tests in parallel.

# Handling pytest-xdist

If we disable `pytest-xdist` psutil tests still run, but we get a warning:

```text
psutil/tests/test_testutils.py:367
  ~/svn/psutil/psutil/tests/test_testutils.py:367: PytestUnknownMarkWarning: Unknown pytest.mark.xdist_group - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.xdist_group(name="serial")
```

This warning appears for methods that are intended to run serially, those
decorated with `@pytest.mark.xdist_group(name="serial")`. However, since
`pytest-xdist` is now disabled, the decorator no longer exists. To address
this, I implemented the following solution in `psutil/tests/__init__.py`:

```python
import pytest, functools

PYTEST_PARALLEL = "PYTEST_XDIST_WORKER" in os.environ  # True if running parallel tests

if not PYTEST_PARALLEL:
    def fake_xdist_group(*_args, **_kwargs):
        """Mimics `@pytest.mark.xdist_group` decorator. No-op: it just
        calls the test method or return the decorated class."""
        def wrapper(obj):
            @functools.wraps(obj)
            def inner(*args, **kwargs):
                return obj(*args, **kwargs)

            return obj if isinstance(obj, type) else inner

        return wrapper

    pytest.mark.xdist_group = fake_xdist_group  # monkey patch
```

With this in place the warning disappears when running tests serially. To run
tests in parallel, we'll manually enable `xdist`:

```text
$ python3 -m pytest -p xdist -n auto --dist loadgroup
```

# Disable some default plugins

pytests also loads quite a bunch of plugins by default (see output of `pytest
--trace-config --collect-only`). I tried to disable some of them with:

```
pytest -p no:junitxml -p no:doctest -p no:nose -p no:pastebin
```

...but that didn't make much of a difference.

# Optimizing test collection time

By default, pytest searches the entire directory for tests, adding unnecessary
overhead. In `pyproject.toml` you can tell pytest where test files
are located:

```toml
[tool.pytest.ini_options]
testpaths = ["psutil/tests/"]
```

With this I saved another 0.03 seconds. Before:

```text
$ python3 -m pytest --collect-only
...
======================== 685 tests collected in 0.20s =========================
```

After:

```text
$ python3 -m pytest --collect-only
...
======================== 685 tests collected in 0.17s =========================
```

# Putting it all together

With these small optimizations, I managed to reduce `pytest` startup time by
~0.12 seconds, bringing it down from 0.42 seconds. While this improvement is
insignificant for full test runs, it somewhat makes a noticeable difference
when repeatedly running individual tests from the command line, which is
something I do frequently during development. Final result is visible in
[PR-2538](https://github.com/giampaolo/psutil/pull/2538).

# Other links which may be useful

* [https://github.com/zupo/awesome-pytest-speedup](https://github.com/zupo/awesome-pytest-speedup)
* [https://projects.gentoo.org/python/guide/pytest.html](https://projects.gentoo.org/python/guide/pytest.html)
