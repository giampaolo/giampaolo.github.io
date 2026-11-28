"""Sets `reading_time` (minutes) on each post. Code blocks are not counted."""

import html.parser
import math

from pelican import signals
from pelican.contents import Article

WPM = 200


class WordCounter(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.words = 0
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag == "pre":
            self.skip += 1

    def handle_endtag(self, tag):
        if tag == "pre" and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.words += len(data.split())


def reading_minutes(html):
    parser = WordCounter()
    parser.feed(html)
    return max(1, math.ceil(parser.words / WPM))


def set_reading_time(content):
    if isinstance(content, Article):
        content.reading_time = reading_minutes(content._content)


def register():
    signals.content_object_init.connect(set_reading_time)
