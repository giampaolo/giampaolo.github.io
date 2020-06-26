Source code for https://giampaolo.github.io/.
Dev branch is `gh-pages` while `master` is never touched and only stores the generated HTML content.

Make a new blog post
====================

* under `gh-pages`, create a new file, e.g. `content/blog/2020/new-blog-post.rst`:

```
New blog post
#############

:date: 2020-06-26
:tags: announce, python

Hello world!
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
`blog post <../../2013/making-constants-part-of-your-api-is-evil/>`_
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
