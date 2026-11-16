#!/usr/bin/env python3

"""Regenerate content/contributions.rst, the page listing the pull
requests I made to other people's projects. Data comes from the
GitHub search API, using the token in ~/.github.api.key.

Run it via `make update-contributions`.
"""

import argparse
import json
import os
import re
import urllib.parse
import urllib.request

USER = "giampaolo"
TOKEN_FILE = os.path.expanduser("~/.github.api.key")
OUTPUT = os.path.join("content", "contributions.rst")

# hand-picked, anything not listed here is rendered as minor
MAJOR = {
    "btimby/fulltext": {46, 49, 52, 62},
    "btimby/reloadconf": {9},
    "felix-hilden/sphinx-codeautolink": {196, 197, 205},
    "numpy/numpy": {30583},
    "PyCQA/autoflake": {107},
    "pytest-dev/pytest": {14874},
    "pytest-dev/pytest-subtests": {199},
    "python/cpython": {1030, 7160, 7874, 11784, 12271, 144047},
    "sphinx-doc/sphinx": {14816},
    "tornadoweb/tornado": {295},
}

# replace the GitHub title
TITLES = {
    "python/cpython": {
        1030: "`selectors`: make `modify()` faster for poll-like selectors",
        7160: (
            "`shutil`: efficient zero-copy file copy (Linux, macOS, Windows)"
        ),
        7874: "`shutil.copytree()`: speedup by using `os.scandir()` cache",
        11784: "add `socket.create_server()`",
        12271: "`unittest`: add `--durations` option to show slowest tests",
        144047: (
            "`subprocess`: use efficient event-driven `Popen.wait()` on"
            " Linux / macOS / BSD"
        ),
    },
}

# always the first section
PINNED = "python/cpython"

# closed without being merged, shown anyway
INCLUDE = {
    "numpy/numpy": {30583},
    "pytest-dev/pytest": {14874},
    "tornadoweb/tornado": {295},
}

# never shown
EXCLUDE = {
    "packagecontrol/channel": {30, 31},
    "python/peps": {733},
    "python/planet": {417, 643},
    "saulomeirelles/WomenInPython": {15},
    "Veristack/libstemmer": {1},
    "Veristack/xxHash": {1},
}

# pre-GitHub CPython work, from `git log`. A title makes it major.
BPO = [
    ("2014-06-14", 6916, None),
    ("2014-06-11", 17552, "add `socket.sendfile()`"),
    ("2014-04-29", 13248, None),
    ("2014-04-04", 21076, "turn `signal` module constants into enums"),
    ("2014-03-20", 18931, "`selectors`: support `/dev/poll` on Solaris"),
    ("2013-10-20", 16038, None),
    ("2013-05-21", 17996, None),
    ("2013-05-16", 17992, None),
    ("2013-04-17", 17707, None),
    (
        "2013-04-10",
        17675,
        "make socket `repr()` show local and remote addresses",
    ),
    ("2013-03-18", 17452, None),
    ("2013-02-25", 17197, None),
    (
        "2012-12-31",
        10527,
        "`multiprocessing`: use `poll()` instead of `select()` if available",
    ),
    ("2012-12-17", 16646, None),
    ("2012-10-19", 16270, None),
    ("2012-10-17", 16264, None),
    ("2012-05-15", 14807, None),
    ("2012-05-14", 14800, None),
    ("2012-03-22", 10340, None),
    ("2012-03-20", 13694, None),
    (
        "2011-12-14",
        13449,
        "`sched`: add `blocking` parameter to `scheduler.run()`",
    ),
    ("2011-12-14", 8684, "`sched`: make `scheduler` class thread-safe"),
    ("2011-12-10", 13563, None),
    ("2011-07-23", 11049, None),
    ("2011-07-01", 12442, "add `shutil.disk_usage()`"),
    ("2011-06-27", 12139, None),
    ("2011-05-07", 12002, None),
    ("2011-05-06", 11072, "`ftplib`: add MLSD command support (RFC 3659)"),
    ("2011-03-15", 11289, None),
    ("2011-03-03", 11351, None),
    ("2011-03-03", 11265, None),
    ("2011-03-03", 9795, None),
    ("2011-02-28", 11348, None),
    ("2011-02-28", 8594, None),
    ("2011-02-25", 11323, None),
    ("2011-02-25", 11291, None),
    ("2011-02-25", 11232, None),
    ("2011-02-25", 11214, None),
    ("2011-02-25", 11177, None),
    ("2011-02-25", 10882, "add `os.sendfile()`"),
    ("2011-02-25", 10784, "add `os.getpriority()` and `os.setpriority()`"),
    ("2010-10-04", 6706, "`asyncore`: add `handle_accepted()` method"),
    ("2010-09-08", 9794, "add context manager protocol to `socket.socket`"),
    ("2010-09-01", 9693, None),
    ("2010-08-30", 9711, None),
    ("2010-08-29", 9706, None),
    ("2010-08-23", 9601, None),
    ("2010-08-21", 9129, None),
    ("2010-08-17", 8866, None),
    ("2010-08-17", 8807, None),
    ("2010-08-14", 8857, None),
    ("2010-08-04", 8687, None),
    ("2010-08-04", 6822, None),
    ("2010-08-04", 2944, None),
    ("2010-06-30", 6589, None),
    ("2010-05-26", 8806, "`ftplib`: add SSL contexts support"),
    ("2010-05-18", 8573, None),
    ("2010-05-10", 8490, None),
    (
        "2010-05-10",
        4972,
        "`ftplib`: add context manager protocol to `FTP` class",
    ),
    ("2010-04-29", 8543, None),
    ("2010-04-19", 4841, None),
    ("2010-04-18", 3817, None),
    ("2009-11-15", 2054, "`ftplib`: add `FTP_TLS` class (FTP over TLS)"),
    ("2008-10-11", 4088, None),
    ("2008-09-27", 3939, None),
    ("2008-03-13", 2055, None),
    ("2008-03-13", 1960, None),
    ("2008-02-07", 2026, None),
    ("2008-02-06", 1959, None),
    ("2008-01-26", 1938, None),
]

HEADER = """\
Contributions
#############

Patches and pull requests I contributed to other people's projects over \
the years. For my own work see the `About </about>`_ page.
"""


def parse_cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()


def fetch_prs():
    with open(TOKEN_FILE) as f:
        token = f.read().strip()
    prs = []
    page = 1
    while True:
        query = urllib.parse.urlencode({
            "q": f"type:pr author:{USER} -user:{USER}",
            "per_page": 100,
            "page": page,
        })
        req = urllib.request.Request(
            f"https://api.github.com/search/issues?{query}",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
        )
        with urllib.request.urlopen(req) as resp:
            data = json.load(resp)
        prs.extend(data["items"])
        if not data["items"] or len(prs) >= data["total_count"]:
            return prs
        page += 1


def is_merged(pr):
    return bool(pr["pull_request"].get("merged_at"))


def rst_escape(text):
    # `code` in a GitHub title becomes ``code``
    parts = text.strip().split("`")
    if len(parts) % 2 == 0:
        return re.sub(r"([`*|_\\])", r"\\\1", text.strip())
    out = []
    for i, part in enumerate(parts):
        if i % 2:
            out.append(f"``{part}``")
        else:
            out.append(re.sub(r"([*|_\\])", r"\\\1", part))
    return "".join(out)


def pr_line(pr):
    date = pr["created_at"][:10]
    line = f"* {date} "
    label = pr_label(pr)
    title = pr["title"]
    # "gh-83069: ..." / "bpo-4080: ..." titles are labelled by issue
    m = re.match(r"((?:gh|bpo)-\d+)[\s:/]*", title, flags=re.IGNORECASE)
    if m:
        label = m.group(1).lower()
        title = title[m.end() :]
    title = TITLES.get(repo_name(pr), {}).get(pr["number"], title)
    line += f"`{label} <{pr['html_url']}>`__: "
    line += rst_escape(title)
    return line + status(pr)


def repo_name(pr):
    return pr["repository_url"].split("/repos/")[1]


def is_included(pr):
    return pr["number"] in INCLUDE.get(repo_name(pr), ())


def status(pr):
    if is_merged(pr):
        return ""
    if pr["state"] == "open":
        return " *(open)*"
    return " *(not merged)*"


def is_excluded(pr):
    return pr["number"] in EXCLUDE.get(repo_name(pr), ())


def pr_label(pr):
    if "bpo" in pr:
        return f"bpo-{pr['number']}"
    return f"#{pr['number']}"


def bpo_entries():
    entries = []
    for date, number, title in BPO:
        entries.append({
            "bpo": True,
            "number": number,
            "title": title,
            "created_at": date,
            "html_url": f"https://bugs.python.org/issue{number}",
            "repository_url": "https://api.github.com/repos/python/cpython",
            "pull_request": {"merged_at": date},
        })
    return entries


def is_major(pr):
    if "bpo" in pr:
        return bool(pr["title"])
    return pr["number"] in MAJOR.get(repo_name(pr), ())


def minor_line(prs):
    links = []
    for pr in prs:
        links.append(f"`{pr_label(pr)} <{pr['html_url']}>`__" + status(pr))
    return "* Minor: " + ", ".join(links)


def pr_block(prs):
    major = [pr for pr in prs if is_major(pr)]
    minor = [pr for pr in prs if not is_major(pr)]
    out = [pr_line(pr) for pr in major]
    if minor:
        out.append(minor_line(minor))
    out.append("")
    return out


def render(prs):
    by_repo = {}
    for pr in prs:
        by_repo.setdefault(repo_name(pr), []).append(pr)
    for repo_prs in by_repo.values():
        repo_prs.sort(key=lambda pr: pr["created_at"], reverse=True)

    # most recently touched projects first
    repos = sorted(
        by_repo,
        key=lambda repo: (repo == PINNED, by_repo[repo][0]["created_at"]),
        reverse=True,
    )

    out = [HEADER]
    for repo in repos:
        repo_prs = by_repo[repo]
        # projects with only minor stuff are left out
        if not any(is_major(pr) for pr in repo_prs):
            continue
        title = f"`{repo} <https://github.com/{repo}>`__"
        out.append(title)
        out.append("-" * len(title))
        out.append("")
        out.extend(pr_block(repo_prs))

    return "\n".join(out)


def main():
    prs = [
        pr
        for pr in fetch_prs()
        if (is_merged(pr) or pr["state"] == "open" or is_included(pr))
        and not is_excluded(pr)
    ]
    bpo = bpo_entries()
    with open(OUTPUT, "w") as f:
        f.write(render(prs + bpo))
    print(
        f"wrote {len(prs)} pull requests and {len(bpo)} bpo issues to {OUTPUT}"
    )


if __name__ == "__main__":
    parse_cli()
    main()
