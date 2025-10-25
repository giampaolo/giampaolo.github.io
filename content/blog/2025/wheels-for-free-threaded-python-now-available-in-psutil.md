Title: Wheels for free-threaded Python now available in psutil
Date: 2025-10-25
Tags: psutil, python, wheels
Authors: Giampaolo Rodola

With the release of psutil 7.1.2, wheels for free-threaded Python are now
available. This milestone was achieved mostly through a community effort, as
several internal refactorings to the C code were required to make it possible
(see
[issue #2565](https://github.com/giampaolo/psutil/issues/2565#issuecomment-2910225647)).
Many of these changes were contributed by
[Lysandros Nikolaou](https://github.com/lysnikolaou). Thanks to him for the
effort and for bearing with me during code reviews!

## What is free-threaded Python?

Free-threaded Python (available since **Python 3.13**) refers to Python builds
that are compiled with the **GIL (Global Interpreter Lock) disabled**, allowing
true parallel execution of Python bytecodes across multiple threads. This is
particularly beneficial for CPU-bound applications, as it enables better
utilization of multi-core processors.

## The state of free-threaded wheels

According to Hugo van Kemenade's [free-threaded wheels
tracker](https://hugovk.github.io/free-threaded-wheels/), the adoption of
free-threaded wheels among the **top 360 most-downloaded PyPI packages with C
extensions** is still limited. Out of these 360 packages only **128** provide
wheels that are compiled for free-threaded Python, meaning they can run on
Python builds with the GIL disabled. This illustrates that while progress has
been made, most popular packages with C extensions **still do not offer
ready-made wheels for free-threaded Python**.

## What it means for library authors to provide wheels

When a library author provides a wheel, users can install a pre-compiled binary
package without having to build it from source. This is especially important
for packages with C extensions, like psutil, which is largely written in C.
These packages often have complex build requirements and depend on a working C
compiler. Providing wheels therefore makes installation far simpler and is
effectively essential for the users of that particular package.

Currently, universal wheels for free-threaded Python don't exist. Each wheel
must be built specifically for a Python version and its GIL configuration. For
example, authors need to create separate wheels for Python 3.13 and 3.14,
ensuring their C extensions are compatible with free-threaded Python.

In practical terms, this means that on each release you have to distribute *a lot* of files:

```
psutil-7.1.2-cp313-cp313t-macosx_10_13_x86_64.whl
psutil-7.1.2-cp313-cp313t-macosx_11_0_arm64.whl
psutil-7.1.2-cp313-cp313t-manylinux2010_x86_64.manylinux_2_12_x86_64.manylinux_2_28_x86_64.whl
psutil-7.1.2-cp313-cp313t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl
psutil-7.1.2-cp313-cp313t-win_amd64.whl
psutil-7.1.2-cp313-cp313t-win_arm64.whl
psutil-7.1.2-cp314-cp314t-macosx_10_15_x86_64.whl
psutil-7.1.2-cp314-cp314t-macosx_11_0_arm64.whl
psutil-7.1.2-cp314-cp314t-manylinux2010_x86_64.manylinux_2_12_x86_64.manylinux_2_28_x86_64.whl
psutil-7.1.2-cp314-cp314t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl
psutil-7.1.2-cp314-cp314t-win_amd64.whl
psutil-7.1.2-cp314-cp314t-win_arm64.whl
```

A **true universal wheel** would greatly reduce this overhead, allowing a
single wheel to support multiple Python versions and platforms. Hopefully,
**Python 3.15** will simplify this process. Two competing proposals, [PEP
803](https://www.python.org/dev/peps/pep-0803/) and [PEP
809](https://www.python.org/dev/peps/pep-0809/), are meant to solve this
problem: allowing a **single wheel to cover multiple Python versions and
platforms**. That would drastically reduce distribution complexity for library
authors.

## How to install free-threaded psutil

You can now install psutil for free-threaded Python directly via `pip`:

```bash
pip install psutil --only-binary=:all:
```

This ensures you get the **pre-compiled** wheels without triggering a source
build.
