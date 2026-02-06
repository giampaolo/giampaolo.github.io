#!/usr/bin/env python3

"""Convert a Pelican RST blog post to Pelican MD format.

Usage: python convert.py content/blog/2020/new-website.rst
"""

import os
import re
import subprocess
import sys


def parse_rst(filepath):
    with open(filepath) as f:
        content = f.read()

    lines = content.split("\n")

    # Extract title (first line, followed by a line of #, =, -, etc.)
    title = None
    body_start = 0
    if (
        len(lines) >= 2
        and lines[1]
        and all(c == lines[1][0] for c in lines[1].strip())
    ):
        title = lines[0].strip()
        body_start = 2
    elif (
        len(lines) >= 3
        and lines[0]
        and all(c == lines[0][0] for c in lines[0].strip())
    ):
        # overline style
        title = lines[1].strip()
        body_start = 3

    # Extract metadata (:date:, :tags:, :slug:, etc.)
    metadata = {}
    i = body_start
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        m = re.match(r"^:(\w+):\s*(.*)", line)
        if m:
            metadata[m.group(1).lower()] = m.group(2).strip()
            i += 1
        else:
            break

    body = "\n".join(lines[i:])
    return title, metadata, body


def rst_body_to_md(rst_body):
    """Use pandoc to convert RST body to markdown."""
    result = subprocess.run(
        [
            "pandoc",
            "-f",
            "rst",
            "-t",
            (
                "markdown_strict+backtick_code_blocks"
                "+fenced_code_attributes-raw_html"
            ),
            "--wrap=none",
        ],
        input=rst_body,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("pandoc stderr: %s" % result.stderr, file=sys.stderr)
    return result.stdout


def fix_md_output(md_text):
    """Post-process pandoc output to clean up over-escaping."""
    # ``` {.python} -> ```python
    md_text = re.sub(r"``` \{\.(\w+)\}", r"```\1", md_text)
    md_text = re.sub(r"``` \{\.(\w+) .*?\}", r"```\1", md_text)

    # Remove unnecessary backslash escaping outside of code blocks.
    parts = re.split(r"(```[^\n]*\n.*?\n```)", md_text, flags=re.DOTALL)
    for idx in range(0, len(parts), 2):  # even indices = prose
        # \`...\` -> `...`
        parts[idx] = re.sub(r"\\`([^`\n]+?)\\`", r"`\1`", parts[idx])
        parts[idx] = parts[idx].replace("\\`", "`")
        parts[idx] = parts[idx].replace("\\_", "_")
        parts[idx] = parts[idx].replace("\\[", "[")
        parts[idx] = parts[idx].replace("\\]", "]")
        parts[idx] = parts[idx].replace("\\#", "#")
        parts[idx] = parts[idx].replace("\\*", "*")
        parts[idx] = parts[idx].replace("\\@", "@")
    md_text = "".join(parts)

    return md_text


def convert_file(rst_path):
    title, metadata, body = parse_rst(rst_path)
    md_body = rst_body_to_md(body)
    md_body = fix_md_output(md_body)

    # Build MD header
    header_lines = []
    if title:
        header_lines.append("Title: %s" % title)
    if "date" in metadata:
        header_lines.append("Date: %s" % metadata["date"])
    if "tags" in metadata:
        header_lines.append("Tags: %s" % metadata["tags"])
    if "slug" in metadata:
        header_lines.append("Slug: %s" % metadata["slug"])
    header_lines.append("Authors: Giampaolo Rodola")

    md_content = "\n".join(header_lines) + "\n\n" + md_body.lstrip("\n")

    # git mv .rst -> .md, then overwrite with converted content
    md_path = rst_path.rsplit(".rst", 1)[0] + ".md"
    subprocess.check_call(["git", "mv", rst_path, md_path])
    with open(md_path, "w") as f:
        f.write(md_content)
    print("%s -> %s" % (rst_path, md_path))


def main():
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".rst"):
        print("Usage: python convert.py <file.rst>", file=sys.stderr)
        sys.exit(1)
    rst_path = sys.argv[1]
    if not os.path.isfile(rst_path):
        print("File not found: %s" % rst_path, file=sys.stderr)
        sys.exit(1)
    convert_file(rst_path)


if __name__ == "__main__":
    main()
