#!/usr/bin/env python3

import argparse
import datetime
import os

LOREM = """\
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""

MD_TEMPLATE = """\
Title: My title
Date: {}
Slug: my-title
Tags: psutil, python
Authors: Giampaolo Rodola

""" + LOREM

RST_TEMPLATE = """\
My title
########

:date: {}
:tags: psutil, python
:slug: my-title

""" + LOREM

TEMPLATES = {"md": MD_TEMPLATE, "rst": RST_TEMPLATE}

FORMAT = None


def parse_cli():
    global FORMAT
    parser = argparse.ArgumentParser(
        description="Create a new blog post template."
    )
    parser.add_argument("format", choices=sorted(TEMPLATES))
    args = parser.parse_args()
    FORMAT = args.format


def main():
    parse_cli()
    now = datetime.datetime.now()
    root = os.path.join("content", "blog", str(now.year))
    os.makedirs(root, exist_ok=True)
    ext = "." + FORMAT
    while True:
        fname = input(f"file name (e.g. new-blog-post{ext}): ")
        if fname and fname.endswith(ext):
            break
    file = os.path.join(root, fname)
    with open(file, "w") as f:
        f.write(TEMPLATES[FORMAT].format(now.strftime("%Y-%m-%d")))
    print(f"{file!r} was created")


if __name__ == "__main__":
    main()
