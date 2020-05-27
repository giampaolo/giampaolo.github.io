#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Giampaolo Rodola'
SITENAME = 'Giampaolo Rodola'
SITESUBTITLE = 'Python enthusiast, core developer, psutil author'
SITEURL = ''
TWITTER_USERNAME = 'grodola'
THEME = 'theme'

PATH = 'content'

TIMEZONE = 'Europe/Rome'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Social widget
SOCIAL = (
    ('github', 'http://github.com/giampaolo'),
    ('linkedin', 'https://www.linkedin.com/in/grodola/'),
    ('twitter', 'https://twitter.com/grodola'),
)

DEFAULT_PAGINATION = 5

# --- menu

DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_PAGES_ON_MENU = False
MENUITEMS = (
    ('Donate', '/pages/donate.html'),
    ('About', '/pages/about.html'),
)

ARTICLE_PATHS = ['blog']
ARTICLE_URL = 'blog/{date:%Y}/{slug}/'
ARTICLE_SAVE_AS = 'blog/{date:%Y}/{slug}.html'

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True
