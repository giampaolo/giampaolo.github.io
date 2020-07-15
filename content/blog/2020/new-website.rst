New Pelican website
###################

:date: 2020-06-26
:tags: announce, python, pelican, psutil

Hello there. I present you my new blog / personal website!
This is something I've been wanting to do for a very long time, since the old blog hosted at https://grodola.blogspot.com/ was... well, too old. =)
This new site is based on `Pelican <https://docs.getpelican.com/en/stable/>`__, a static website generator similar to `Jekyll <https://jekyllrb.com/>`__. Differently from Jekyll, it uses Python instead of Ruby, and that's why I chose it. It's minimal, straight to the point and I feel I have control of things. This is what Pelican gave me out of the box:

* blog functionality
* ability to write content by using reStructuredText
* RSS & Atom feed
* easy integration with GitHub pages
* ability to add comments via Disqus

To this I added a mailing list (I used feedburner), so that users can subscribe and receive an email every time I make a new blog post. As you can see the website is very simple, but it's exactly what I wanted (minimalism). As for the domain name I opted for `gmpy.dev <https://gmpy.dev/>`__, mostly because I know my name is hard to type and pronounce for non-english speakers. And also because I couldn't come up with a better name. ;)

GIT-based workflow
==================

The main reason why I blogged so rarely over the years was mostly because blogger.com provided me no way to edit content in RsT or markdown, and the lack of GIT integration. This made me lazy. With Pelican + GitHub pages the workflow to create and publish new content is very straightforward. I use 2 branches: `gh-pages <https://github.com/giampaolo/giampaolo.github.io/tree/gh-pages>`__, which is the source code of this web-site, and `master <https://github.com/giampaolo/giampaolo.github.io/tree/master>`__, which is where the generated HTML content lives and it is being served by GitHub pages. This is what I do when I have to create a new blog post:

* under `gh-pages` branch I create a new file, e.g. `content/blog/2020/new-blog-post.rst`:

.. code-block:: rst

    New blog post
    #############

    :date: 2020-06-26
    :tags: announce, python

    Hello world!

* commit it:

.. code-block:: text

    git add content/blog/2020/new-blog-post.rst
    git ci -am "new blog post"
    git push

* publish it:

.. code-block:: text

    make github

Within 1 minute or something, GitHub will automatically serve `gmpy.dev <https://gmpy.dev/>`__ with the updated content. And this is why I think I will start blogging more often. =)
The core of Pelican is `pelicanconf.py <https://github.com/giampaolo/giampaolo.github.io/blob/gh-pages/pelicanconf.py>`__, which lets you customize a lot of things by remaining independent from the theme. I still ended up modifying the default theme though, writing a customized "archives" view and editing CSS to make the site look better on mobile phones. All in all, I am very satisfied with Pelican, and I'm keen on recommending it to anyone who doesn't need dynamism.

About me
========

I spent most of last year (2019) in China, dating my girlfriend, remote working from a shared office space in Shenzhen, and I even taught some Python to a class of Chinese folks with no previous programming experience. The course was about the basics of the language + basic filesystem operations, and the most difficult thing to explain was indentation. I guess that shows the difference between knowing a language and knowing how to teach it.

I got back to Italy in December 2020, just before the pandemic occurred. Because of my connections with China, I knew about the incoming pandemic sooner than the rest of my friends, which for a while (until the lockdown) made them think I was crazy. =)

Since I knew I would be stuck at home for a long time, I bought a quite nice acoustic guitar (Taylor) after many years, and resumed playing (and singing). I learned a bunch of new songs, mostly about Queen, including Bohemian Rhapsody, which is something I've been wanting to do since forever.

I also spent some time working on a personal project that I'm keeping private for the moment, something to speed up file copies, which follows the experiments I made in `BPO-33671 <https://bugs.python.org/issue33671>`__. It's still very beta, but I managed to make file copies around 170% faster compared to ``cp`` command on Linux, which is pretty impressive (and I think I can push it even further). I will blog about that once I'll have something more solid / stable. Most likely it'll become my next OSS project, even tough I have mixed feelings about that, since the amount of time I'm devoting to psutil is already a lot.

Speaking of which, today I'm also releasing `psutil 5.7.1 <https://groups.google.com/forum/#!topic/psutil/zT0jUE2IaE4>`__, which adds support for **Windows Nano**.

I guess this is all. Cheers and subscribe!
