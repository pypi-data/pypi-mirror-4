from django.conf.urls.defaults import *
from django.views.generic import TemplateView

from vellum.feeds import BlogPostsFeed, BlogPostsByCategory
from vellum.views import *

urlpatterns = patterns('',
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
        view=PostView.as_view(),
        name='vellum_detail'
    ),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{1,2})/$',
        view=PostDayArchiveView.as_view(),
        name='vellum_archive_day'
    ),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$',
        view=PostMonthArchiveView.as_view(),
        name='vellum_archive_month'
    ),
    url(r'^(?P<year>\d{4})/$',
        view=PostYearArchiveView.as_view(),
        name='vellum_archive_year'
    ),
    url(r'^categories/(?P<slug>[-\w]+)/$',
        view=CategoryDetailView.as_view(),
        name='vellum_category_detail'
    ),
    url(r'^categories/$',
        view=CategoryListView.as_view(),
        name='vellum_category_list'
    ),
    url(r'^tags/(?P<slug>[-\w]+)/$',
        view=TagDetailView.as_view(),
        name='vellum_tag_detail'
    ),
    url(r'^tags/$',
        view=TemplateView.as_view(template_name='vellum/tag_list.html'),
        name='vellum_tag_list'
    ),
    url(r'^search/$',
        view=search,
        name='vellum_search'
    ),
    url(r'^archives/$',
        view=PostArchiveView.as_view(),
        name='vellum_archives'
    ),
    url(r'^feed/categories/(?P<slug>[^/]+)/$',
        view=BlogPostsByCategory(),
        name='vellum_feed_category'
    ),
    url(r'^feed/$',
        view=BlogPostsFeed(),
        name='vellum_feed_latest'
    ),
    url(r'^$',
        view=PostIndexView.as_view(),
        name='vellum'
    ),
)
