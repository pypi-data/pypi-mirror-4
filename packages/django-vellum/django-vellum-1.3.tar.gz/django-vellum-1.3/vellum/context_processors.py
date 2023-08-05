from vellum import settings


def blog_settings(request):
    """
    Add blog settings to the context, making them available to templates.
    """
    return {
        'BLOG_NAME': settings.BLOG_NAME,
        'BLOG_DESCRIPTION': settings.BLOG_DESCRIPTION,
        'BLOG_EXCERPTLENGTH': settings.BLOG_EXCERPTLENGTH,
        'BLOG_USEDISQUS': settings.BLOG_USEDISQUS,
    }
