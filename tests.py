import shlex
import shutil
import subprocess
import tempfile
import unittest


def sh(cmd):
    subprocess.check_call(shlex.split(cmd))


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
