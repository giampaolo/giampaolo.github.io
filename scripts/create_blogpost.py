#!/usr/bin/env python3

import os
import datetime

MD_TEMPLATE = """\
Title: My title
Date: {}
Tags: psutil, python
Authors: Giampaolo Rodola

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""

RST_TEMPLATE = """\
title
#####
:date: {}
:tags: psutil, python

"""


def main():
    now = datetime.datetime.now()
    root = os.path.join("content", "blog", str(now.year))
    os.makedirs(root, exist_ok=True)
    while True:
        fname = input("file name (e.g. new-blog-post.md): ")
        if fname and fname.endswith(".md"):
            break
    file = os.path.join(root, fname)
    with open(file, "w") as f:
        f.write(MD_TEMPLATE.format(now.strftime("%Y-%m-%d")))
    print(f"{file!r} was created")


if __name__ == "__main__":
    main()
