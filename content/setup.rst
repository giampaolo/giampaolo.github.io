Setup
#####

This is the software I use on a daily basis. Despite being a Linux user for
almost 20 years, I'm not what you'd call an advanced desktop Linux user. I'm a
minimalist, and my setup is extremely simple: I spend most of my day in 2
programs, the editor and the terminal, and that's where most of the
customization goes. The rest is just scripts to automate the Linux installation
and a bunch of key bindings to switch desktops and resize windows, since I tend
to avoid the mouse whenever I can.

Hardware
--------

* 💻 **Laptop**: `ASUS Zenbook Pro 16X`_ (UX7602VI), Intel i9-13900H, 32 GB RAM,
  NVIDIA RTX 4070
* ⌨️ **Keyboard**: `Keychron Q1 V2`_, US ANSI layout, blue (clicky) switches

System
------

* 🐧 **OS**: Linux Mint + KDE, fully automated and reproducible via my (still
  unpublished) dotfiles repo. Linux user since 2008, always on Debian-based
  distros.
* ✏️ **Editor**: `Sublime Text`_ (since 2010), heavily customized (about 31k
  lines of my own Python plugins). I'm a `fanboy`_. I think it's the best piece
  of software ever written, and `I happily pay for the license`_.
* 🖥️ **Terminal**: `kitty`_ (since 2026), customized via Python plugins to make
  it work like Sublime Text (tabs, projects, sessions, same key bindings, etc.)
* 💲 **Shell**: bash
* 🛠️ **Build**: a ``Makefile`` in every project
* 🔀 **Git**: the base CLI, with GPG-signed commits and tags, `delta`_ for
  diffs, and `git-crypt`_ for encrypting secrets. Mostly used from Sublime
  Text, via my own plugins.
* 📦 **Other OSes**: `VirtualBox`_ + `Vagrant`_ VMs to develop psutil on
  Windows, FreeBSD, NetBSD, OpenBSD and SunOS. For macOS and AIX I use
  `cfarm`_.
* 🌐 **Browser**: `Brave`_ (since 2021)
* 🧰 **CLI tools**: `bat`_, `duf`_ and `eza`_ (aliased to ``cat``, ``df`` and
  ``ls``), `ripgrep`_, `htop`_, `ncdu`_
* ⚙️ **CI**: GitHub Actions + `cibuildwheel`_, plus a few psutil bots
  (`issue triage`_, `anti AI slop`_, `changelog`_)
* 📚 **Docs**: reStructuredText + `Sphinx`_ with a custom theme and
  `custom plugins`_ (see `psutil.io`_). `Pelican`_ for this site.

Python
------

* 🐞 **Shell**: `IPython`_, `pdb++`_, `colored-traceback`_
* 🧪 **Tests**: `pytest`_, with `pytest-xdist`_ and `pytest-instafail`_
* 🧹 **Linters / formatters** (on every project): Python: `black`_ + `ruff`_
  everywhere, occasionally `vulture`_ (to delete dead code). Others:
  `clang-format`_ (C), `rstcheck`_ and `rstwrap`_ (reST, the latter written by
  me), `toml-sort`_ (TOML), `markdownlint`_ (Markdown), `shellcheck`_ and
  `shfmt`_ (shell), `dprint`_ (JSON, YAML).

AI
--

* 💬 **First AI ever tried**: Grok and ChatGPT via web, November 2025
* 🤖 **First coding agent**: Claude Code, January 2026 (€18/month subscription)
* ⚡ **Now using**: Claude Code Max (5x). Anthropic `gave me 6 free months`_ of
  Max 20x for psutil.

Screenshots
-----------

Sublime Text:

.. image:: /images/setup-sublime-text.webp
  :target: /images/setup-sublime-text.webp
  :alt: Sublime Text, with psutil source code on the left and a git log on the right

kitty:

.. image:: /images/setup-kitty.webp
  :target: /images/setup-kitty.webp
  :alt: kitty, with a git log and bat showing psutil code

KDE desktop:

.. image:: /images/setup-desktop.webp
  :target: /images/setup-desktop.webp
  :alt: KDE desktop, with a custom top panel

.. _`anti AI slop`: https://github.com/giampaolo/psutil/blob/04ffb994682ac8bf5101a21b001683eb266e06a3/.github/workflows/anti_slop.py
.. _`ASUS Zenbook Pro 16X`: https://www.asus.com/us/laptops/for-creators/zenbook/zenbook-pro-16x-oled-ux7602/
.. _`bat`: https://github.com/sharkdp/bat
.. _`black`: https://github.com/psf/black
.. _`Brave`: https://brave.com/
.. _`cfarm`: https://portal.cfarm.net/
.. _`changelog`: https://github.com/giampaolo/psutil/blob/04ffb994682ac8bf5101a21b001683eb266e06a3/.github/workflows/changelog_bot.py
.. _`cibuildwheel`: https://github.com/pypa/cibuildwheel
.. _`clang-format`: https://clang.llvm.org/docs/ClangFormat.html
.. _`colored-traceback`: https://github.com/staticshock/colored-traceback.py
.. _`custom plugins`: https://github.com/giampaolo/psutil/tree/04ffb994682ac8bf5101a21b001683eb266e06a3/docs/_ext
.. _`delta`: https://github.com/dandavison/delta
.. _`git-crypt`: https://github.com/AGWA/git-crypt
.. _`dprint`: https://dprint.dev/
.. _`duf`: https://github.com/muesli/duf
.. _`eza`: https://github.com/eza-community/eza
.. _`fanboy`: https://forum.sublimetext.com/t/does-sublime-text-reach-vlc-era/78415/3?u=giampaolo
.. _`gave me 6 free months`: https://x.com/grodola/status/2029688743162957847
.. _`htop`: https://htop.dev/
.. _`I happily pay for the license`: https://x.com/grodola/status/1511046542760845312
.. _`IPython`: https://ipython.org/
.. _`issue triage`: https://github.com/giampaolo/psutil/blob/04ffb994682ac8bf5101a21b001683eb266e06a3/.github/workflows/triage.py
.. _`Keychron Q1 V2`: https://www.keychron.com/products/keychron-q1
.. _`kitty`: https://sw.kovidgoyal.net/kitty/
.. _`markdownlint`: https://github.com/markdownlint/markdownlint
.. _`ncdu`: https://dev.yorhel.nl/ncdu
.. _`pdb++`: https://github.com/pdbpp/pdbpp
.. _`Pelican`: https://pelican.dev/
.. _`psutil.io`: https://psutil.io/
.. _`pytest-instafail`: https://github.com/pytest-dev/pytest-instafail
.. _`pytest-xdist`: https://github.com/pytest-dev/pytest-xdist
.. _`pytest`: https://pytest.org/
.. _`ripgrep`: https://github.com/BurntSushi/ripgrep
.. _`rstcheck`: https://github.com/rstcheck/rstcheck
.. _`rstwrap`: https://github.com/giampaolo/rstwrap
.. _`ruff`: https://github.com/astral-sh/ruff
.. _`shellcheck`: https://github.com/koalaman/shellcheck
.. _`shfmt`: https://github.com/mvdan/sh
.. _`Sphinx`: https://www.sphinx-doc.org/
.. _`Sublime Text`: https://www.sublimetext.com/
.. _`toml-sort`: https://github.com/pappasam/toml-sort
.. _`Vagrant`: https://developer.hashicorp.com/vagrant
.. _`VirtualBox`: https://www.virtualbox.org/
.. _`vulture`: https://github.com/jendrikseipp/vulture
