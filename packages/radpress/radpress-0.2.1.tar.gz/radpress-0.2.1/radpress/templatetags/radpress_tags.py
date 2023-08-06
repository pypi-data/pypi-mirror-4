from django import template
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe
from docutils.core import publish_parts
from docutils.parsers.rst import directives
from radpress.rst_directives import Pygments, More
from radpress import settings as radpress_settings

register = template.Library()


@register.filter
def restructuredtext(value):
    parts = publish_parts(
        source=smart_str(value), writer_name='html',
        settings_overrides=radpress_settings.RST_SETTINGS)

    return mark_safe(force_unicode(parts['html_body']))

restructuredtext.is_safe = True
directives.register_directive('sourcecode', Pygments)
directives.register_directive('more', More)


@register.inclusion_tag('radpress/_head.html')
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


@register.inclusion_tag('radpress/_datetime.html')
def radpress_datetime(datetime):
    """
    Time format that compatible with html5.

    Arguments:
    - `datetime`: datetime.datetime
    """
    context = {'datetime': datetime}
    return context
