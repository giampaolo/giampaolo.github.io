"""Pelican plugin adding the Sphinx roles used by psutil.io blog posts.

Lets us copy posts from psutil's docs/blog/ as they are. Cross-refs
(:func:, :term:, :ref:, :doc:, ...) are resolved against the Sphinx
inventories in inventories/, refreshed by "make update-inventories".
"""

import logging
import os
import re
import zlib

from docutils import nodes
from docutils.parsers.rst import roles

logger = logging.getLogger(__name__)

HERE = os.path.dirname(os.path.abspath(__file__))
INVENTORIES = (
    ("https://psutil.io/", os.path.join(HERE, "inventories", "psutil.inv")),
    (
        "https://docs.python.org/3/",
        os.path.join(HERE, "inventories", "python.inv"),
    ),
)
# from psutil's docs/conf.py
EXTLINKS = {
    "gh": ("https://github.com/giampaolo/psutil/issues/%s", "#%s"),
    "pr": ("https://github.com/giampaolo/psutil/pull/%s", "PR-%s"),
    "user": ("https://github.com/%s", "@%s"),
    "commit": ("https://github.com/giampaolo/psutil/commit/%s", "%s"),
    "pypi": ("https://pypi.org/project/psutil/%s/", "%s"),
    "bpo": ("https://bugs.python.org/issue%s", "BPO-%s"),
    "cpy": ("https://github.com/python/cpython/issues/%s", "cpython/#%s"),
    "cpy-pr": ("https://github.com/python/cpython/pull/%s", "cpython/PR-%s"),
    "src": ("https://github.com/giampaolo/psutil/blob/master/%s", "%s"),
}
MANPAGES_URL = "https://manpages.debian.org/{path}"
PROC_URL = "https://manpages.debian.org/{}(5)"

PY_ROLES = ("func", "meth", "class", "exc", "mod", "data", "attr", "obj")
# Sphinx matches these case-insensitively
CASELESS = ("std:term", "std:label")
INV_LINE_RE = re.compile(r"(.+?)\s+(\S+)\s+(-?\d+)\s+?(\S*)\s+(.*)")
TITLE_RE = re.compile(r"^(.+?)\s*<([^<]*?)>$", re.DOTALL)

# {(kind, name): (url, dispname)}, kind is "py" or e.g. "std:term"
OBJECTS = {}


def load_inventory(base_url, path):
    with open(path, "rb") as f:
        data = f.read()
    header = data.split(b"\n", 4)
    if header[0] != b"# Sphinx inventory version 2":
        msg = f"{path}: unsupported inventory format"
        raise ValueError(msg)
    for line in zlib.decompress(header[4]).decode().splitlines():
        m = INV_LINE_RE.match(line.rstrip())
        if not m:
            continue
        name, kind, _, uri, dispname = m.groups()
        if uri.endswith("$"):
            uri = uri[:-1] + name
        if dispname == "-":
            dispname = name
        if kind.startswith("py:"):
            kind = "py"
        elif kind in CASELESS:
            name = name.lower()
        # first inventory wins, like local refs over intersphinx
        OBJECTS.setdefault((kind, name), (base_url + uri, dispname))


def split_title(text):
    m = TITLE_RE.match(text)
    if m:
        return True, m.group(1), m.group(2)
    return False, text, text


def unresolved(inliner, lineno, rawtext):
    source = inliner.document.get("source", "?")
    logger.warning("%s:%s: unresolved reference %s", source, lineno, rawtext)


def link(rawtext, url, text, literal):
    child = nodes.literal(text=text) if literal else nodes.Text(text)
    ref = nodes.reference(rawtext, "", refuri=url)
    ref += child
    return ref


def py_role(name, rawtext, text, lineno, inliner, options=None, content=None):
    has_title, title, target = split_title(text)
    if not has_title:
        title = target.lstrip("~.")
        if target.startswith("~"):
            title = title.rsplit(".", 1)[-1]
        if name in {"func", "meth"} and not title.endswith(")"):
            title += "()"
    target = target.lstrip("~.")
    # blog posts are read with ".. currentmodule:: psutil"
    for candidate in (target, "psutil." + target):
        hit = OBJECTS.get(("py", candidate))
        if hit:
            return [link(rawtext, hit[0], title, literal=True)], []
    unresolved(inliner, lineno, rawtext)
    return [nodes.literal(rawtext, title)], []


def c_func_role(
    name, rawtext, text, lineno, inliner, options=None, content=None
):
    has_title, title, target = split_title(text)
    if not has_title:
        title = target + "()"
    hit = OBJECTS.get(("c:function", target))
    if hit:
        return [link(rawtext, hit[0], title, literal=True)], []
    unresolved(inliner, lineno, rawtext)
    return [nodes.literal(rawtext, title)], []


def make_std_role(kind):
    def role(name, rawtext, text, lineno, inliner, options=None, content=None):
        has_title, title, target = split_title(text)
        key = target.lower() if kind in CASELESS else target
        if kind == "std:doc":
            # psutil's posts only use absolute doc paths
            key = key.lstrip("/")
        hit = OBJECTS.get((kind, key))
        if not hit:
            unresolved(inliner, lineno, rawtext)
            return [nodes.Text(title)], []
        if not has_title and kind != "std:term":
            title = hit[1]
        return [link(rawtext, hit[0], title, literal=False)], []

    return role


def make_extlink_role(url, caption):
    def role(name, rawtext, text, lineno, inliner, options=None, content=None):
        has_title, title, part = split_title(text)
        if not has_title:
            title = caption % part
        return [nodes.reference(rawtext, title, refuri=url % part)], []

    return role


def manpage_role(
    name, rawtext, text, lineno, inliner, options=None, content=None
):
    url = MANPAGES_URL.format(path=text)
    ref = nodes.reference(rawtext, "", refuri=url)
    ref += nodes.emphasis(text=text, classes=["manpage"])
    return [ref], []


def field_role(
    name, rawtext, text, lineno, inliner, options=None, content=None
):
    return [nodes.literal(rawtext, text, classes=["ntuple-field"])], []


# ported from psutil's docs/_ext/proc_role.py
def proc_role(
    name, rawtext, text, lineno, inliner, options=None, content=None
):
    path = text.strip()
    # /proc/[pid]/stat -> proc_pid_stat
    parts = []
    for seg in path.lstrip("/").split("/"):
        s = seg.strip("[]").lower()
        parts.append("pid" if s == "pid" else s)
    url = PROC_URL.format("_".join(parts))
    ref = nodes.reference(rawtext, "", refuri=url, classes=["proc"])
    ref += nodes.literal(text=path)
    return [ref], []


def register():
    for base_url, path in INVENTORIES:
        load_inventory(base_url, path)
    for name in PY_ROLES:
        roles.register_local_role(name, py_role)
    roles.register_local_role("c:func", c_func_role)
    roles.register_local_role("term", make_std_role("std:term"))
    roles.register_local_role("ref", make_std_role("std:label"))
    roles.register_local_role("doc", make_std_role("std:doc"))
    for name, (url, caption) in EXTLINKS.items():
        roles.register_local_role(name, make_extlink_role(url, caption))
    roles.register_local_role("manpage", manpage_role)
    roles.register_local_role("field", field_role)
    roles.register_local_role("proc", proc_role)
