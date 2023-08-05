django-vellum
=============

A [Django](http://www.djangoproject.com/) web log application.


Genesis
-------

This application began life as part of [Nathan Borror](http://nathanborror.com/)'s [django-basic-apps](https://github.com/nathanborror/django-basic-apps), a collection of simple prebuilt Django applications.

When I first decided I wanted to move to a Django-based blog, I looked around to see if there were any existing projects I could use. There was certainly no shortage of blog applications, but none of them were exactly what I was looking for. Nathan's basic blog was close, but, as the name implies, very basic. [Kevin Fricovsky](http://montylounge.com/)'s [django-mingus](https://github.com/montylounge/django-mingus), which is itself built on top of Nathan's basic blog, appealed to me the most, but still had aspects that I did not like. So I decided to create my own.

In true open source fashion, I forked django-basic-apps. It provided an excellent framework to work from -- had I started from scratch, I would have ended up recreating a lot of what Nathan had already done. With that fork, along with some ideas inspired by django-mingus and Wordpress, I was able to craft a blog application that suited me perfectly. I think it's pretty nice -- and it turns out it suits some other people pretty well, too!

The only thing I did not like about it was that the blog was part of a larger collection of Django applications, most of which I did not use. I am happy to put my name on the blog, but I did not want to maintain or vouch for the numerous other apps. So, I spun off the two other applications that I did use ([django-media](https://github.com/pigmonkey/django-media) and [django-inlineobjects](https://github.com/pigmonkey/django-inlineobjects)), deleted the rest, and renamed the blog.

Thus, django-[vellum](https://en.wikipedia.org/wiki/Vellum).


Features
--------


### Wordpress Import

A management script is included to import blog posts from a Wordpress-generated XML file. For more information, run `./manage.py wordpress_import`.


### Disqus

[Disqus](https://disqus.com/) comments are supported (and recommended).


### Auto-Excerpts

An author can manually specify content to use as the excerpt or tease of a post. If they choose not to do this, auto excerpts can be enabled to automatically truncate a post after a certain number of characters and use that as the post excerpt.


### Markup

Posts can be written in traditional HTML, plaintext, or any number of markup languages ([Markdown](http://daringfireball.net/projects/markdown/) is recommended).

If Markdown is used, an enjoyable writing experience is provided by [django-wmd](https://github.com/pigmonkey/django-wmd/).


Requirements
------------

* [django-inlineobjects](https://github.com/pigmonkey/django-inlineobjects) is required for including content objects inside of blog posts.
* [django-simplesearch](https://github.com/pigmonkey/django-simplesearch) is required for searching posts.
* [django-taggit](https://github.com/alex/django-taggit) is required for tagging.
* [django-taggit-templatetags](https://github.com/feuervogel/django-taggit-templatetags) is required for generating a tag cloud.
* [django-markup](https://github.com/bartTC/django-markup/>) is required for markup language support.
* The [Python Markdown library](http://packages.python.org/Markdown/) is required for Markdown support. (Markdown support can be disabled, but it is the default choice. If the user does not specify otherwise, all posts are put through Markdown.)
* The [Django comment framework](https://docs.djangoproject.com/en/dev/ref/contrib/comments/) must be installed, unless Disqus support is enabled (see below).


### Suggested

The following packages are not required, but are suggested to take full advantage of django-vellum.

* [django-disqus](http://github.com/arthurk/django-disqus) is suggested for [Disqus](https://disqus.com/)-powered comments.
* [smartypants](http://pypi.python.org/pypi/smartypants) is suggested for smart typography (curly quotes, en- and em-dashes, ellipses, etc.).
* [django-wmd](https://github.com/pigmonkey/django-wmd/) is suggested for an enhanced [Markdown](http://daringfireball.net/projects/markdown/) experience.
* [django-media](https://github.com/pigmonkey/django-media) may be used in conjuction with (the previously mentioned) django-inlineobjects to include photos in posts.


Installation
------------

django-vellum is available on PyPI and can be installed with PIP.

    pip install django-vellum

Alternatively, you may download the source and install it.

    python setup.py install


Setup
-----

1. Add `vellum` to your `settings.INSTALLED_APPS`.
2. Add `vellum.context_processors.blog_settings` to your `settings.TEMPLATE_CONTEXT_PROCESSORS`.


Questions
---------

If you have any questions, or encounter any issues, email me at [pm@pig-monkey.com](mailto:pm@pig-monkey.com).

Full documentation is coming, I promise!
