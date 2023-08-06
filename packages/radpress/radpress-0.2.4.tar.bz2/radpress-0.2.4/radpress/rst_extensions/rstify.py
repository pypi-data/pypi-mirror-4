"""
Copied and modified from django-rstify extension.
"""

from docutils.core import publish_parts
from docutils.writers import html4css1
from django.utils.encoding import force_unicode, smart_str
from radpress.settings import RST_SETTINGS
from radpress.rst_extensions import register_directives

# register radpress customized directives
register_directives()


class TextutilsHTMLWriter(html4css1.Writer):
    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = TextutilsHTMLTranslator


class TextutilsHTMLTranslator(html4css1.HTMLTranslator):

    def __init__(self, document):
        html4css1.HTMLTranslator.__init__(self, document)

    def visit_admonition(self, node, name=''):
        self.body.append(self.starttag(
            node, 'div', CLASS=(name or 'admonition')))
        self.set_first_last(node)

    def visit_footnote(self, node):
        self.body.append(self.starttag(node, 'p', CLASS='footnote'))
        self.footnote_backrefs(node)

    def depart_footnote(self, node):
        self.body.append('</p>\n')

    def visit_label(self, node):
        self.body.append(self.starttag(
            node, 'strong', '[%s' % self.context.pop(), CLASS='label'))

    def depart_label(self, node):
        self.body.append('</a>]</strong> %s' % self.context.pop())


def rstify(text, language_code='en'):
    settings = {
        'initial_header_level': 1,
        'doctitle_xform': False,
        'language_code': language_code,
        'footnote_references': 'superscript',
        'trim_footnote_reference_space': True,
        'default_reference_context': 'view',
        'link_base': '',
    }
    settings.update(RST_SETTINGS)

    parts = publish_parts(
        source=smart_str(text),
        writer=TextutilsHTMLWriter(),
        settings_overrides=settings)

    return force_unicode(parts['body'])  # or fragment?
