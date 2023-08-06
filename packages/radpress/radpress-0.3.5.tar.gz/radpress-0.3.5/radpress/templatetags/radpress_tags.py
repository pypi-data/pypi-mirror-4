from django import template
from django.conf import settings
from django.contrib.sites.models import Site
from django.template import Node, TemplateSyntaxError
from django.utils.safestring import mark_safe
from radpress import settings as radpress_settings, get_version
from radpress.compat import User
from radpress.models import Article
from radpress.rst_extensions.rstify import rstify

register = template.Library()


@register.filter()
def restructuredtext(text):
    """
    Convert rst content to html markup language in template files.
    """
    return mark_safe(rstify(text))


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


@register.simple_tag
def radpress_static_url(path):
    """
    Receives Radpress static urls.
    """
    version = get_version()
    return '%sradpress/%s?ver=%s' % (settings.STATIC_URL, path, version)


@register.filter
def radpress_full_name(user):
    if not isinstance(user, User):
        full_name = ''

    else:
        full_name = user.get_full_name()

        if not full_name:
            full_name = user.username

    return full_name
