Source code for https://gmpy.dev/ / https://giampaolo.github.io/. Dev branch is
[gh-pages](https://github.com/giampaolo/giampaolo.github.io/tree/gh-pages).
`master` branch is never touched and only stores the auto-generated HTML
content based off of `gh-pages` branch.

Setup
=====

* Install python deps:

```
make install-pydeps
```

* Run server locally (http://127.0.0.1:8000):

```
make serve
```

Make a new blog post
====================

* under `gh-pages`, create a new file, e.g. `content/blog/2020/new-blog-post.rst`; use `make create-blogpost`

```
New blog post
#############

:date: 2020-06-26
:tags: announce, python

Hello world!
```

* test it:

```bash
# after this connect to http://127.0.0.1:8000/
make clean html serve
```

* commit it:

```bash
git add content/blog/2020/new-blog-post.rst
git ci -am "new blog post"
git push
```

* publish it:

```bash
make github
```

* within 1 minute or something, GitHub will automatically update gmpy.dev content.

Link to an internal blog post
=============================

```
`blog post <../2013/making-constants-part-of-your-api-is-evil>`_
```

Image
=====

```
.. raw:: html

    <div>
        <a href="/images/me-with-jay.jpg">
        <img src="/images/me-with-jay.jpg" style="width:750px; height:500px" />
        </a>
    </div>
```
