#!/usr/bin/env python3

# Copyright (c) 2009 Giampaolo Rodola'. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""This gets executed on 'git commit' and rejects the commit in case
the submitted code does not pass validation. Validation is run only
against the files which were modified in the commit. Install this with
"make install-git-hook".
"""


import os
import shlex
import subprocess
import sys


PYTHON = sys.executable
PY3 = sys.version_info[0] >= 3
THIS_SCRIPT = os.path.realpath(__file__)


def term_supports_colors():
    try:
        import curses

        assert sys.stderr.isatty()
        curses.setupterm()
        assert curses.tigetnum("colors") > 0
    except Exception:  # noqa: BLE001
        return False
    return True


def hilite(s, ok=True, bold=False):
    """Return an highlighted version of 'string'."""
    if not term_supports_colors():
        return s
    attr = []
    if ok is None:  # no color
        pass
    elif ok:  # green
        attr.append("32")
    else:  # red
        attr.append("31")
    if bold:
        attr.append("1")
    return "\x1b[%sm%s\x1b[0m" % (";".join(attr), s)


def exit(msg):
    print(hilite("commit aborted: " + msg, ok=False), file=sys.stderr)
    sys.exit(1)


def sh(cmd):
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise RuntimeError(stderr)
    if stderr:
        print(stderr, file=sys.stderr)
    if stdout.endswith("\n"):
        stdout = stdout[:-1]
    return stdout


def open_text(path):
    kw = {"encoding": "utf8"} if PY3 else {}
    return open(path, **kw)


def git_commit_files():
    out = sh(["git", "diff", "--cached", "--name-only"])
    py_files = [
        x for x in out.split("\n") if x.endswith(".py") and os.path.exists(x)
    ]
    rst_files = [
        x for x in out.split("\n") if x.endswith(".rst") and os.path.exists(x)
    ]
    return (py_files, rst_files)


def black(files):
    print("running black (%s)" % len(files))
    cmd = [PYTHON, "-m", "black", "--check", "--safe"] + files
    if subprocess.call(cmd) != 0:
        return exit(
            "Python code didn't pass 'ruff' style check."
            "Try running 'make fix-ruff'."
        )


def ruff(files):
    print("running ruff (%s)" % len(files))
    cmd = [PYTHON, "-m", "ruff", "check", "--no-cache"] + files
    if subprocess.call(cmd) != 0:
        return exit(
            "Python code didn't pass 'ruff' style check."
            "Try running 'make fix-ruff'."
        )


def rstcheck(files):
    print("running rst linter (%s)" % len(files))
    cmd = ["rstcheck", "--config=pyproject.toml"] + files
    if subprocess.call(cmd) != 0:
        return sys.exit("RST code didn't pass style check")


def main():
    py_files, rst_files = git_commit_files()
    if py_files:
        black(py_files)
        ruff(py_files)
    if rst_files:
        rstcheck(rst_files)


main()
