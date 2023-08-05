from django.contrib.syndication.views import FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.models import Comment
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from vellum import settings
from vellum.models import Post, Category


class BlogPostsFeed(Feed):
    _site = Site.objects.get_current()
    title = _site.name
    description = settings.BLOG_DESCRIPTION

    def link(self):
        return reverse('vellum')

    def items(self):
        return Post.objects.published()[:settings.BLOG_FEEDSIZE]

    def item_description(self, item):
        if settings.BLOG_FEEDEXCERPTS and item.excerpt:
            return '%s %s' % (item.excerpt, render_to_string('vellum/includes/post_more.html', {'post': item}))
        return item.body_rendered

    def item_pubdate(self, obj):
        return obj.publish


class BlogPostsByCategory(Feed):

    def get_object(self, request, slug):
        return Category.objects.get(slug__exact=slug)

    def title(self, obj):
        _site = Site.objects.get_current()
        return '%s: %s' % (_site.name, obj.title)

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def description(self, obj):
        return "Posts recently categorized as %s" % obj.title

    def items(self, obj):
        return obj.post_set.published()[:settings.BLOG_FEEDSIZE]

    def item_description(self, item):
        if settings.BLOG_FEEDEXCERPTS and item.excerpt:
            return '%s %s' % (item.excerpt, render_to_string('vellum/includes/post_more.html', {'post': item}))
        return item.body_rendered

    def item_pubdate(self, obj):
        return obj.publish


class CommentsFeed(Feed):
    _site = Site.objects.get_current()
    title = '%s comment feed' % _site.name
    description = '%s comments feed.' % _site.name

    def link(self):
        return reverse('vellum')

    def items(self):
        ctype = ContentType.objects.get_for_model(Post)
        return Comment.objects.filter(content_type=ctype)[:settings.BLOG_FEEDSIZE]

    def item_pubdate(self, obj):
        return obj.submit_date
