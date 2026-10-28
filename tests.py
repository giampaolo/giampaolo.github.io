import subprocess
import unittest


def sh(cmd):
    subprocess.check_call(cmd, shell=True)


class TestSuite(unittest.TestCase):

    def setUp(self):
        sh("make clean")

    def tearDown(self):
        sh("make clean")

    def test_make_html(self):
        sh("make html")

    def test_make_build_prod(self):
        sh("make build-prod")
