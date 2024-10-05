#!/usr/bin/env python3

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys

sys.path.append(os.curdir)
from pelicanconf import *

SITEURL = "https://gmpy.dev"
RELATIVE_URLS = False
DELETE_OUTPUT_DIRECTORY = True

# Following items are often useful when publishing
# DISQUS_SITENAME = ""
# GOOGLE_ANALYTICS = ""
