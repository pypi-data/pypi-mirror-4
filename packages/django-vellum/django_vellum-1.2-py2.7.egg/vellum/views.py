from django.db.models import F
from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic import (ListView, DetailView, ArchiveIndexView,
                                  DateDetailView, DayArchiveView,
                                  MonthArchiveView, YearArchiveView)

from simplesearch.functions import *
from taggit.models import Tag

from vellum.models import *
from vellum import settings as blog_settings


class PostIndexView(ArchiveIndexView):
    """Display all blog posts."""
    queryset = Post.objects.public()
    date_field = 'publish'
    paginate_by = blog_settings.BLOG_PAGESIZE
    template_name = 'vellum/post_list.html'


class PostArchiveView(ArchiveIndexView):
    """Display all blog posts on a single page."""
    queryset = Post.objects.public()
    date_field = 'publish'


class PostYearArchiveView(YearArchiveView):
    """Display all blog posts in a given year."""
    queryset = Post.objects.public()
    date_field = 'publish'
    paginate_by = blog_settings.BLOG_PAGESIZE
    make_object_list = True


class PostMonthArchiveView(MonthArchiveView):
    """Display all blog posts in a given month."""
    queryset = Post.objects.public()
    date_field = 'publish'
    paginate_by = blog_settings.BLOG_PAGESIZE

    def get_month_format(self):
        """
        Allow both 3-letter month abbreviations and month as a decimal number.
        """
        if len(self.get_month()) < 3:
            self.month_format = '%m'
        return self.month_format


class PostDayArchiveView(DayArchiveView):
    """Display all blog posts in a given day."""
    queryset = Post.objects.public()
    date_field = 'publish'
    paginate_by = blog_settings.BLOG_PAGESIZE

    def get_month_format(self):
        """
        Allow both 3-letter month abbreviations and month as a decimal number.
        """
        if len(self.get_month()) < 3:
            self.month_format = '%m'
        return self.month_format


class PostView(DateDetailView):
    """Display a blog post."""
    model = Post
    date_field = 'publish'

    def get_allow_future(self):
        """
        Allow super users to view posts with a publish date in the future.
        """
        if self.request.user.is_superuser:
            self.allow_future = True
        return self.allow_future

    def get_month_format(self):
        """
        Allow both 3-letter month abbreviations and month as a decimal number.
        """
        if len(self.get_month()) < 3:
            self.month_format = '%m'
        return self.month_format

    def get_object(self):
        # Call the superclass.
        object = super(PostView, self).get_object()
        # If the user isn't super and the post is not public, do not allow
        # viewing.
        if not self.request.user.is_superuser and object.status != 2:
            raise Http404
        # If the user's IP is not specified as internal, increase the post's
        # view count.
        if not self.request.META.get('REMOTE_ADDR') in blog_settings.BLOG_INTERNALIPS:
            object.visits = F('visits') + 1
            object.save()
        return object


class CategoryListView(ListView):
    """Display a list of categories."""
    model = Category


class CategoryDetailView(ListView):
    """Display all blog posts in a given category."""
    paginate_by = blog_settings.BLOG_PAGESIZE

    def category(self, **kwargs):
        return get_object_or_404(Category, slug=self.kwargs['slug'])

    def get_queryset(self, **kwargs):
        return Post.objects.published().filter(categories=self.category)

    def get_template_names(self, **kwargs):
        return 'vellum/category_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context.
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        # Add the category to the context.
        context['category'] = self.category
        return context


class TagDetailView(ListView):
    """Display all blog posts with a given tag."""
    paginate_by = blog_settings.BLOG_PAGESIZE

    def tag(self, **kwargs):
        return get_object_or_404(Tag, slug=self.kwargs['slug'])

    def get_queryset(self, **kwargs):
        return Post.objects.published().filter(tags=self.tag)

    def get_template_names(self, **kwargs):
        return 'vellum/tag_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context.
        context = super(TagDetailView, self).get_context_data(**kwargs)
        # Add in the tag to the context.
        context['tag'] = self.tag
        return context


def search(request, template_name='vellum/post_search.html',
           search_fields=['title', 'body', 'tags__name', 'categories__title']):
    """
    Search for blog posts.

    This template will allow you to setup a simple search form that will return
    results based on given search keywords.

    Template: ``vellum/post_search.html``
    Context:
        object_list
            List of blog posts that match given search term(s).
        search_term
            Given search term.
        message
            A message returned by the search.
    """
    context = {}
    message = ''
    query_string = ''

    if 'q' in request.GET:
        query_string = request.GET['q']
        entry_query = get_query(query_string, search_fields)

        try:
            results = Post.objects.published().filter(entry_query).distinct()
            if results:
                context = {'object_list': results, 'search_term': query_string}
            else:
                message = 'No results found! Please try a different search term.'
        except TypeError:
            message = 'Search term was too vague, please try again.'

        context['message'] = message

    return render_to_response(template_name, context,
                              context_instance=RequestContext(request))
