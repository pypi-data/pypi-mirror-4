"""
I copied this script from birkenfeld's pygments-main repository, and edited for
my needs.

:copyright: Copyright 2006-2013 by the Pygments team, see AUTHORS.
:license: BSD, see LICENSE for details.
"""

from docutils import nodes
from docutils.parsers.rst import directives, Directive
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer
from .style_solarized import SolarizedStyle

COMMON_SETTINGS = {
    'noclasses': False,
    'style': SolarizedStyle,
}
DEFAULT = HtmlFormatter(**COMMON_SETTINGS)
VARIANTS = {'linenos': HtmlFormatter(linenos=True, **COMMON_SETTINGS)}


class Pygments(Directive):
    """
    Source code syntax hightlighting.
    """
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = dict([(key, directives.flag) for key in VARIANTS])
    has_content = True

    def run(self):
        self.assert_has_content()

        try:
            lexer = get_lexer_by_name(self.arguments[0])

        except ValueError:
            lexer = TextLexer()

        formatter = (
            self.options and VARIANTS[self.options.keys()[0]] or DEFAULT)
        parsed = highlight(u'\n'.join(self.content), lexer, formatter)

        return [nodes.raw('', parsed, format='html')]
