import html.parser
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
import urllib.parse

from pelicanconf import SITEURL

HERE = os.path.dirname(os.path.abspath(__file__))
RESUME_YAML = os.path.join(HERE, "resume", "resume.yaml")


def sh(cmd):
    subprocess.check_call(shlex.split(cmd))


class LinkParser(html.parser.HTMLParser):

    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.links.append(value)


def resolve_link(outdir, page, link):
    url = urllib.parse.urljoin(SITEURL + "/" + page, link)
    if not url.startswith(SITEURL + "/"):
        return None  # external
    path = urllib.parse.urlsplit(url).path.lstrip("/")
    path = urllib.parse.unquote(path)
    base = os.path.join(outdir, path)
    for candidate in (base, base + ".html", os.path.join(base, "index.html")):
        if os.path.isfile(candidate):
            return candidate
    return False


class TestSuite(unittest.TestCase):

    # don't touch output/, "make autoreload" serves from there
    def setUp(self):
        self.outdir = tempfile.mkdtemp(prefix="pelican-test-")

    def tearDown(self):
        shutil.rmtree(self.outdir)

    def test_make_html(self):
        sh(f"make html OUTPUTDIR={self.outdir}")

    def test_make_build_prod(self):
        sh(f"make build-prod OUTPUTDIR={self.outdir}")

    def test_internal_links(self):
        sh(f"make html OUTPUTDIR={self.outdir}")
        broken = []
        for root, _, files in os.walk(self.outdir):
            for name in files:
                if not name.endswith(".html"):
                    continue
                fpath = os.path.join(root, name)
                page = os.path.relpath(fpath, self.outdir)
                parser = LinkParser()
                with open(fpath, encoding="utf8") as f:
                    parser.feed(f.read())
                for link in parser.links:
                    if link.startswith(("#", "mailto:", "javascript:")):
                        continue
                    if resolve_link(self.outdir, page, link) is False:
                        broken.append(f"{page}: {link}")
        assert broken == []

    def test_build_resume(self):
        with open(RESUME_YAML, "rb") as f:
            if f.read(9) == b"\0GITCRYPT":
                self.skipTest("resume.yaml is encrypted")
        out = os.path.join(self.outdir, "resume.html")
        sh(f"{sys.executable} resume/build.py --html {out}")
        assert os.path.getsize(out) > 0
