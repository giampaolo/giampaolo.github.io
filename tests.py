import datetime
import html.parser
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
import urllib.parse

import docutils.core

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


class TestSphinxRoles(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, os.path.join(HERE, "plugins"))
        import sphinx_roles

        sphinx_roles.register()

    def render(self, text):
        return docutils.core.publish_parts(text, writer="html")["body"]

    def test_py_role(self):
        html = self.render(":meth:`Process.wait`")
        assert 'href="https://psutil.io/api/#psutil.Process.wait"' in html

    def test_manpage_role(self):
        html = self.render(":manpage:`select(2)`")
        assert 'href="https://manpages.debian.org/select(2)"' in html


class TestReadtime(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, os.path.join(HERE, "plugins"))

    def test_code_not_counted(self):
        import readtime

        text = "<p>" + "word " * 401 + "</p>"
        code = "<pre><code>" + "x " * 10000 + "</code></pre>"
        assert readtime.reading_minutes(text + code) == 3


class TestRelatedPosts(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, os.path.join(HERE, "plugins"))

    def make_posts(self, *tag_lists):
        posts = []
        for i, tags in enumerate(tag_lists):
            post = types.SimpleNamespace(
                tags=[types.SimpleNamespace(name=t) for t in tags],
                date=datetime.datetime(2020, 1, 1 + i),
            )
            posts.append(post)
        return posts

    def test_rare_tag_wins(self):
        import related_posts

        # "python" is on every post, "bsd" only on two
        filler = [["python", f"tag{i}"] for i in range(18)]
        posts = self.make_posts(["python", "bsd"], ["python", "bsd"], *filler)
        related_posts.set_related(types.SimpleNamespace(articles=posts))
        assert posts[0].related_posts == [posts[1]]
        assert posts[2].related_posts == []

    def test_ignored_tags(self):
        import related_posts

        filler = [[f"tag{i}"] for i in range(18)]
        posts = self.make_posts(["release"], ["release"], *filler)
        related_posts.set_related(types.SimpleNamespace(articles=posts))
        assert posts[0].related_posts == []
