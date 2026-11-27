"""Pelican plugin that sets `related_posts` on each published post.

Posts are related when they share tags. Rare tags weigh more than
common ones (`python` is on almost every post). Tags that say what
kind of post it is, not what it's about, are skipped.
"""

import math

from pelican import signals

IGNORED_TAGS = {"featured", "release", "personal"}
MAX_RELATED = 3
MIN_SCORE = 2.0


def topic_tags(article):
    return {t.name for t in getattr(article, "tags", [])} - IGNORED_TAGS


def set_related(generator):
    posts = [(a, topic_tags(a)) for a in generator.articles]
    counts = {}
    for _, tags in posts:
        for tag in tags:
            counts[tag] = counts.get(tag, 0) + 1
    weights = {tag: math.log(len(posts) / n) for tag, n in counts.items()}

    for article, tags in posts:
        scored = []
        for other, other_tags in posts:
            if other is article:
                continue
            score = sum(weights[t] for t in tags & other_tags)
            if score >= MIN_SCORE:
                # ties go to the post closest in time
                distance = abs((other.date - article.date).total_seconds())
                scored.append((-score, distance, other))
        scored.sort(key=lambda x: (x[0], x[1]))
        article.related_posts = [x[2] for x in scored[:MAX_RELATED]]


def register():
    signals.article_generator_finalized.connect(set_related)
