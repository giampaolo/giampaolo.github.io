#!/usr/bin/env python
# -*- coding: utf-8 -*- #

"""Useful urls:

- EXTRA_PATH_METADATA: https://stackoverflow.com/a/44209338
"""

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

# --- social widget
SOCIAL = (
    ('github', 'http://github.com/giampaolo'),
    ('linkedin', 'https://www.linkedin.com/in/grodola/'),
    ('twitter', 'https://twitter.com/grodola'),
)

# --- menu

DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_PAGES_ON_MENU = False
MENUITEMS = (
    ('Blog', '/'),
    ('Archives', '/archives'),
    ('Donate', '/donate'),
    ('About', '/about'),
)

# --- blog

ARTICLE_PATHS = ['blog']
ARTICLE_URL = 'blog/{date:%Y}/{slug}/'
ARTICLE_SAVE_AS = 'blog/{date:%Y}/{slug}.html'
DEFAULT_PAGINATION = 5

# --- pages

PAGE_PATHS = ['']
PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'

# ---paths

# static paths will be copied without parsing their contents
STATIC_PATHS = [
    'static',
    'images',
    'extra',
]

EXTRA_PATH_METADATA = {
    'extra/favicon.ico': {'path': 'favicon.ico'},
}
DIRECT_TEMPLATES = ['index', 'tags', 'categories', 'archives']

# DEFAULT_DATE_FORMAT = ('%d %b %Y')

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True
