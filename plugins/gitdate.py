"""Pelican plugin that sets `git_updated` on pages (not articles).

It's the date of the last commit touching the source file, shown in
the footer as "Updated YYYY-MM-DD". Needs the full git history: on a
shallow clone every file gets the date of the last commit.
"""

import datetime
import subprocess
import warnings

from pelican import signals
from pelican.contents import Page


def set_git_updated(content):
    # Article is not a Page subclass
    if not isinstance(content, Page) or not content.source_path:
        return
    path = content.source_path
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%cs", "--", path], text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError) as err:
        warnings.warn(f"git log failed for {path}: {err}", stacklevel=1)
        return
    # empty for files not committed yet
    if out:
        content.git_updated = datetime.date.fromisoformat(out)


def register():
    signals.content_object_init.connect(set_git_updated)
