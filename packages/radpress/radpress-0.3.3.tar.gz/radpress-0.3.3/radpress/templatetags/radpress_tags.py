from django import template
from django.utils.safestring import mark_safe
from radpress import settings as radpress_settings
from radpress.models import Article
from radpress.rst_extensions.rstify import rstify

register = template.Library()


@register.filter()
def restructuredtext(text):
    """
    Convert rst content to html markup language in template files.
    """
    return mark_safe(rstify(text))


@register.inclusion_tag('radpress/tags/head.html')
def radpress_include_head():
    """
    Includes radpress css and js files.
    """
    context = {
        'bootstrap': radpress_settings.BOOTSTRAP_CSS,
        'bootstrap_responsive': radpress_settings.BOOTSTRAP_RESPONSIVE_CSS,
        'modernizr': radpress_settings.MODERNIZR
    }

    return context


@register.inclusion_tag('radpress/tags/datetime.html')
def radpress_datetime(datetime):
    """
    Time format that compatible with html5.

    Arguments:
    - `datetime`: datetime.datetime
    """
    context = {'datetime': datetime}
    return context


@register.inclusion_tag('radpress/tags/widget_latest_posts.html')
def radpress_widget_latest_posts():
    """
    Receives latest posts.
    """
    object_limit = radpress_settings.DATA['RADPRESS_LIMIT']
    context = {
        'object_list': Article.objects.all_published()[:object_limit]
    }
    return context