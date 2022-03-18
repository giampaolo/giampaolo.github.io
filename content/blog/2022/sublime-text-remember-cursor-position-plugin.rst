Sublime Text: remember cursor position plugin
#############################################

:date: 2022-03-18
:tags: sublime, python

My editor of choice for Python development is Sublime Text.
It has been for a very long time (10 years).
It's fast, minimalist and straight to the point, which is why I always resisted
the temptation to use more advanced and modern IDEs such as PyCharm or VS code,
which admittedly have superior auto-completion and refactoring tools.

There is a very simple feature I've always missed in ST: the
possibility to "remember" / save the cursor position when a file is closed.
The only plugin promising to do such a thing is called
`BufferScroll <https://github.com/titoBouzout/BufferScroll>`__, but for some
reason it ceased working for me at some point.
I spent a considerable amount of time Googling for an alternative but, to my
surprise, I couldn't find any plugin which implements such a simple feature.
Therefore today I decided to bite the bullet and try to implement this myself,
by writing my first ST plugin, which I paste below.

What it does is this:

* every time a file is closed, save the cursor position (x and y axis) to a JSON file
* if that same file is re-opened, restore the cursor at that position

What's neat about ST plugins is that they are just Python files which you can
install by copying them in ST's config directory. On Linux you can copy the
script below in:

``~/.config/sublime-text-3/Packages/User/cursor_positions.py``

...and will work out of the box.
This is exactly the kind of minimalism which I love about ST, and which I've
always missed in other IDEs.

.. code-block:: python

    # cursor_positions.py

    """
    A plugin for SublimeText which saves (remembers) cursor position when
    a file is closed.
    Install it by copying this file in ~/.config/sublime-text-3/Packages/User/
    directory (Linux).

    Author: Giampaolo Rodola'
    License: MIT
    """

    import datetime
    import json
    import os
    import tempfile
    import threading

    import sublime
    import sublime_plugin


    SUBLIME_ROOT = os.path.realpath(os.path.join(sublime.packages_path(), '..'))
    SESSION_FILE = os.path.join(
        SUBLIME_ROOT, "Local", "cursor_positions.session.json")
    # when reading the session file on startup, we'll remove entries
    # older than X days
    RM_FILE_OLDER_THAN_DAYS = 180


    def log(*args):
        print("    %s: " % os.path.basename(__file__), end="")
        print(*args)


    class Session:

        def __init__(self):
            self._lock = threading.Lock()
            os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
            self.prune_old_entries()

        # --- file

        def read_session_file(self):
            try:
                with self._lock:
                    with open(SESSION_FILE, "r") as f:
                        return json.load(f)
            except (FileNotFoundError, json.decoder.JSONDecodeError):
                return {}

        def write_session_file(self, d):
            # Use the same FS so that the move operation is atomic:
            # https://stackoverflow.com/a/18706666
            with tempfile.NamedTemporaryFile(
                    "wt", delete=False, dir=os.path.dirname(SESSION_FILE)) as f:
                f.write(json.dumps(d, indent=4, sort_keys=True))
            with self._lock:
                os.rename(f.name, SESSION_FILE)

        def prune_old_entries(self):
            old = self.read_session_file()
            new = old.copy()
            now = datetime.datetime.now()
            for file, entry in old.items():
                tstamp = entry["last_update"]
                last_update = datetime.datetime.strptime(
                    tstamp, '%Y-%m-%d %H:%M:%S.%f')
                delta_days = (now - last_update).days
                if delta_days > RM_FILE_OLDER_THAN_DAYS:
                    log("removing old saved file %r" % file)
                    del new[file]
            if new != old:
                self.write_session_file(new)

        # --- operations

        def add_entry(self, file, x, y):
            d = self.read_session_file()
            d[file] = dict(
                x=x,
                y=y,
                last_update=str(datetime.datetime.now()),
            )
            self.write_session_file(d)

        def load_entry(self, file):
            d = self.read_session_file()
            try:
                return d[file]
            except KeyError:
                return None


    session = Session()


    class Events(sublime_plugin.EventListener):

        # --- utils

        @staticmethod
        def get_cursor_pos(view):
            x, y = view.rowcol(view.sel()[0].begin())
            return x, y

        @staticmethod
        def set_cursor_pos(view, x, y):
            pt = view.text_point(x, y)
            view.sel().clear()
            view.sel().add(sublime.Region(pt))
            view.show(pt)

        def save_cursor_position(self, view):
            file_name = view.file_name()
            if file_name is None:
                return  # non-existent file
            log("saving cursor position for %s" % file_name)
            x, y = self.get_cursor_pos(view)
            session.add_entry(file_name, x, y)

        def load_cursor_position(self, view):
            entry = session.load_entry(view.file_name())
            if entry:
                self.set_cursor_pos(view, entry["x"], entry["y"])

        # --- callbacks

        def on_close(self, view):
            # called when a file is closed
            self.save_cursor_position(view)

        def on_load(self, view):
            # called when a file is opened
            self.load_cursor_position(view)
