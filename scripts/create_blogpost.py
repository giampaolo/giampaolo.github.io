#!/usr/bin/env python3

import os
import datetime


def main():
    now = datetime.datetime.now()
    root = os.path.join("content", "blog", str(now.year))
    os.makedirs(root, exist_ok=True)
    while True:
        fname = input("file name (e.g. new-blog-post.rst): ")
        if fname and fname.endswith(".rst"):
            break
    file = os.path.join(root, fname)
    with open(file, "w") as f:
        f.write("title\n")
        f.write("#####\n\n")
        f.write(":date: %s\n" % (now.strftime("%Y-%m-%d")))
        f.write(":tags: psutil, python\n\n")
    print(f"{file!r} was created")


if __name__ == "__main__":
    main()
