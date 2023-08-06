from docutils.parsers.rst import directives
from .directive_pygments import Pygments
from .directive_radpress import More


def register_directives():
    """
    To use directives in your rst system, you should register your custom
    directives.
    """
    directives.register_directive('sourcecode', Pygments)
    directives.register_directive('more', More)
