Source code for https://giampaolo.github.io/.
Dev branch is `gh-pages` while `master` is never touched and only stores the generated HTML content.

Personal notes
==============

* Link to an internal blog post:

```
`blog post <../../2013/making-constants-part-of-your-api-is-evil/>`_
```

* Image:

```
.. raw:: html

    <div>
        <a href="/images/me-with-jay.jpg">
        <img src="/images/me-with-jay.jpg" style="width:750px; height:500px" />
        </a>
    </div>
```

* Separated commas:

```
{% if not loop.last %},{% endif %}
```
