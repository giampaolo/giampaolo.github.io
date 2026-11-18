Source code for <https://gmpy.dev/> website.

On every push to `master` a GitHub Actions workflow builds the Pelican site
and deploys it to GitHub Pages. No generated HTML is stored in the repo.

# Development

```bash
make install-pydeps
make autoreload            # serve on http://127.0.0.1:8000
make create-blogpost-rst   # new post template (RST)
make create-blogpost-md    # new post template (Markdown)
make update-contributions
make lint-all
make test
```

# Comments

[giscus](https://giscus.app/) threads live in
[giampaolo/psutil-blog-comments](https://github.com/giampaolo/psutil-blog-comments),
shared with the [psutil blog](https://psutil.io/blog/). A thread is
matched by post path (`blog/YYYY/slug`), so a post needs the same year
and slug on both sites, and the `GISCUS_*` settings must match psutil's
`docs/conf.py`.
