#!/usr/bin/env python3
import functools

AUTHOR = 'Giampaolo Rodola'
SITENAME = 'Giampaolo Rodola'
SITESUBTITLE = 'Python enthusiast, core developer, psutil author'
SITEURL = ''
TWITTER_USERNAME = 'grodola'
THEME = 'theme'
PATH = 'content'
TIMEZONE = 'Europe/Rome'
DEFAULT_LANG = 'en'
GOOGLE_ANALYTICS = "UA-164357405-2"

# --- atom/rss feeds

FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/{slug}.atom.xml'
FEED_ALL_RSS = 'feeds/all.rss.xml'
CATEGORY_FEED_RSS = 'feeds/{slug}.rss.xml'

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
ARTICLE_URL = 'blog/{date:%Y}/{slug}'
ARTICLE_SAVE_AS = 'blog/{date:%Y}/{slug}.html'
DEFAULT_PAGINATION = 5

# --- pages

PAGE_PATHS = ['']
PAGE_URL = '{slug}'
PAGE_SAVE_AS = '{slug}.html'

# --- tags

TAG_SAVE_AS = 'tags/{slug}.html'
TAG_URL = 'tags/{slug}'

# ---paths

# static paths will be copied without parsing their contents
STATIC_PATHS = [
    'static',
    'images',
    'extra',
    'extra/CNAME',
]

EXTRA_PATH_METADATA = {
    'extra/favicon.ico': {'path': 'favicon.ico'},
    'extra/htaccess': {'path': '.htaccess'},
    'extra/CNAME': {'path': 'CNAME'},
}
DIRECT_TEMPLATES = ['index', 'tags', 'categories', 'archives']

# DEFAULT_DATE_FORMAT = ('%d %b %Y')

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

JINJA_FILTERS = {
    'sort_by_tags': functools.partial(sorted, key=lambda tags: len(tags[1]),
                                      reverse=True)
}

