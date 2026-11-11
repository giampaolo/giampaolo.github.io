Source code for <https://gmpy.dev/> / <https://giampaolo.github.io/>.

Everything lives on the `master` branch. On every push a GitHub Actions
workflow builds the Pelican site and deploys it to GitHub Pages, so no
generated HTML is stored in the repo.

Note: `content/extra/htaccess` is Apache-only and applies to
<https://gmpy.dev/>. GitHub Pages ignores it; the `.github.io` mirror
relies on Pelican's own URL layout.

# Setup

- Install python deps:

```
make install-pydeps
```

- Run server locally (<http://127.0.0.1:8000>):

```
make serve
```

# Make a new blog post

- create a new file, e.g. `content/blog/2020/new-blog-post.rst`; use
  `make create-blogpost`

```
New blog post
#############

:date: 2020-06-26
:tags: announce, python

Hello world!
```

- test it:

```bash
# after this connect to http://127.0.0.1:8000/
make clean html serve
```

- commit and push it:

```bash
git add content/blog/2020/new-blog-post.rst
git ci -am "new blog post"
git push
```

- the push triggers a GitHub Actions build that deploys to Pages; within a
  minute or so gmpy.dev updates automatically.

# Publish

Just push to `master`.

# Comments

[giscus](https://giscus.app/) threads live in
[giampaolo/psutil-blog-comments](https://github.com/giampaolo/psutil-blog-comments),
shared with the [psutil blog](https://psutil.io/blog/). A thread is
matched by post path (`blog/YYYY/slug`), so a post needs the same year
and slug on both sites, and the `GISCUS_*` settings must match psutil's
`docs/conf.py`.

# Link to an internal blog post

```
`blog post <../2013/making-constants-part-of-your-api-is-evil>`_
```

# Image

```
.. raw:: html

    <div>
        <a href="/images/me-with-jay.jpg">
        <img src="/images/me-with-jay.jpg" style="width:750px; height:500px" />
        </a>
    </div>
```
