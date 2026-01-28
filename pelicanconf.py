#!/usr/bin/env python3

import functools

AUTHOR = "Giampaolo Rodola"
SITENAME = "Giampaolo Rodola"
SITESUBTITLE = "Python enthusiast, core developer, psutil author"
SITEURL = "http://127.0.0.1:8000"
TWITTER_USERNAME = "grodola"
THEME = "theme"
PATH = "content"
TIMEZONE = "Europe/Rome"
DEFAULT_LANG = "en"
GOOGLE_ANALYTICS = "UA-164357405-2"

# --- atom / rss feeds (http://127.0.0.1:8000/feeds)
# Planet python uses:
# https://gmpy.dev/feeds/atom.tag.python.xml

FEED_ALL_ATOM = "feeds/atom.all.xml"
FEED_ALL_RSS = "feeds/rss.all.xml"
TAG_FEED_ATOM = "feeds/atom.tag.{slug}.xml"
TAG_FEED_RSS = "feeds/rss.tag.{slug}.xml"

AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
CATEGORY_FEED_ATOM = None
CATEGORY_FEED_RSS = None
TRANSLATION_FEED_ATOM = None
TRANSLATION_FEED_RSS = None

# --- social widget

SOCIAL = (
    ("github", "https://github.com/giampaolo"),
    ("linkedin", "https://www.linkedin.com/in/grodola/"),
    ("twitter", "https://twitter.com/grodola"),
)

# --- menu

DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_PAGES_ON_MENU = False
MENUITEMS = (
    ("Blog", "/"),
    ("Archives", "/archives"),
    ("About", "/about"),
)

# --- blog

ARTICLE_PATHS = ["blog"]
ARTICLE_URL = "blog/{date:%Y}/{slug}"
ARTICLE_SAVE_AS = "blog/{date:%Y}/{slug}.html"
DEFAULT_PAGINATION = 5

# --- pages

PAGE_PATHS = [""]
PAGE_URL = "{slug}"
PAGE_SAVE_AS = "{slug}.html"
# Do not generate /author/* HTML files.
AUTHOR_SAVE_AS = ""
# Do not generate /categories.html
CATEGORIES_SAVE_AS = ""

# --- tags

TAG_SAVE_AS = "tags/{slug}.html"
TAG_URL = "tags/{slug}"

# --- plugins

PLUGIN_PATHS = ["plugins"]
PLUGINS = ["headerid"]

# ---paths

# static paths will be copied without parsing their contents
STATIC_PATHS = [
    "static",
    "images",
    "extra",
    "extra/CNAME",
]

EXTRA_PATH_METADATA = {
    "extra/favicon.ico": {"path": "favicon.ico"},
    "extra/htaccess": {"path": ".htaccess"},
    "extra/CNAME": {"path": "CNAME"},
}
DIRECT_TEMPLATES = ["index", "tags", "categories", "archives"]

# --- others


def month_abbr(dt):
    months = [
        "",
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    return months[dt.month]


JINJA_FILTERS = {
    "sort_by_tags": functools.partial(
        sorted,
        key=lambda tags: (len(tags[1]), -ord(tags[0].name[0])),
        reverse=True,
    ),
    "month_abbr": month_abbr,
}

DEFAULT_DATE_FORMAT = "%d %b %Y"
