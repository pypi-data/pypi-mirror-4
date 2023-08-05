import os.path
import sys
from logging import getLogger
from webhelpers.html import literal
from mako.lookup import TemplateLookup

try:
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import SqlLexer
    from pygments.styles import get_style_by_name
    PYGMENT_STYLE = get_style_by_name('colorful')
    HAVE_PYGMENTS = True
except ImportError: # pragma: no cover
    HAVE_PYGMENTS = False


def render_mako(template_uri, **vars):
    root = os.path.dirname(os.path.abspath(__file__))
    templates_dirs = [root]
    lookup = TemplateLookup(directories=templates_dirs)
    template = lookup.get_template(template_uri)
    return literal(template.render_unicode(**vars))


def db_to_unicode(value):
    try:
        value = unicode(value)
    except (UnicodeDecodeError, UnicodeEncodeError):
        value = "NOT_UNICODE"
    return value


def format_fname(value, _sys_path=None):
    if _sys_path is None:
        _sys_path = sys.path # dependency injection
    # If the value is not an absolute path, the it is a builtin or
    # a relative file (thus a project file).
    if not os.path.isabs(value):
        if value.startswith(('{', '<')):
            return value
        if value.startswith('.' + os.path.sep):
            return value
        return '.' + os.path.sep + value

    # Loop through sys.path to find the longest match and return
    # the relative path from there.
    prefix_len = 0
    value_segs = value.split(os.path.sep)
    for path in _sys_path:
        count = common_segment_count(path.split(os.path.sep), value_segs)
        if count > prefix_len:
            prefix_len = count
    return '%s' % os.path.sep.join(value_segs[prefix_len:])


def format_template_fname(tmpl):
    tmpl_path_parts = tmpl.split('/')
    formatted_fname = literal('&nbsp;/&nbsp;'.join(tmpl_path_parts))
    return formatted_fname


def get_template_inherits(template_obj):
    inherit_obj = getattr(template_obj, 'inherits', None)
    if inherit_obj:
        tmpl_path = format_template_fname(inherit_obj.uri)
        return [tmpl_path] + get_template_inherits(inherit_obj)
    else:
        return []


def common_segment_count(path, value):
    """Return the number of path segments common to both"""
    i = 0
    if len(path) <= len(value):
        for x1, x2 in zip(path, value):
            if x1 == x2:
                i += 1
            else:
                return 0
    return i


def format_sql(query):
    if not HAVE_PYGMENTS: # pragma: no cover
        return unicode(query)

    return unicode(highlight(
        query,
        SqlLexer(encoding='utf-8'),
        HtmlFormatter(
            encoding='utf-8',
            noclasses=True,
            style=PYGMENT_STYLE
        )
    ))


def replace_insensitive(string, target, replacement):
    """Similar to string.replace() but is case insensitive
    Code borrowed from:
    http://forums.devshed.com/python-programming-11/case-insensitive-string-replace-490921.html
    """
    no_case = string.lower()
    index = no_case.rfind(target.lower())
    if index >= 0:
        return string[:index] + replacement + string[index + len(target):]
    else: # no results so return the original string
        return string


logger = getLogger('pylons_debugtoolbar')
