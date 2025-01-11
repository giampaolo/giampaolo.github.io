import unittest
import subprocess


def sh(cmd):
    subprocess.check_call(cmd, shell=True)


class TestSuite(unittest.TestCase):

    def setUp(self):
        sh("make clean")

    def tearDown(self):
        sh("make clean")

    def test_make_html(self):
        sh("make html")

    def test_make_publish(self):
        sh("make publish")
