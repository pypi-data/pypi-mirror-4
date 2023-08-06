from django.conf import settings

DATA = {
    'RADPRESS_TITLE': getattr(settings, 'RADPRESS_TITLE', "Radpress"),
    'RADPRESS_DESCRIPTION': getattr(
        settings, 'RADPRESS_DESCRIPTION',
        "A blogging application for Djangonauts"),
    'RADPRESS_LIMIT': getattr(settings, 'RADPRESS_LIMIT', 5),
    'RADPRESS_GA_CODE': getattr(settings, 'RADPRESS_GA_CODE', None),
    'RADPRESS_DISQUS': getattr(settings, 'RADPRESS_DISQUS', None),
    'RADPRESS_COVER_SIZE': getattr(settings, 'RADPRESS_COVER_SIZE', '652x248')
}

MORE_TAG = '<!-- more -->'
BOOTSTRAP_CSS = getattr(
    settings, 'RADPRESS_BOOTSTRAP_CSS_PATH',
    'radpress/css/bootstrap.min.css')
BOOTSTRAP_RESPONSIVE_CSS = getattr(
    settings, 'RADPRESS_BOOTSTRAP_RESPONSIVE_CSS_PATH', None)
MODERNIZR = getattr(
    settings, 'RADPRESS_MODERNIZR_PATH',
    'radpress/js/modernizr.custom.68944.js')
RST_SETTINGS = getattr(settings, 'RESTRUCTUREDTEXT_FILTER_SETTINGS', {})
RST_SETTINGS.update({
    'initial_header_level': 2,
    'doctitle_xform': True,
    'language_code': 'en',
    'footnote_references': 'superscript',
    'trim_footnote_reference_space': True,
    'default_reference_context': 'view',
    'link_base': '',
})
