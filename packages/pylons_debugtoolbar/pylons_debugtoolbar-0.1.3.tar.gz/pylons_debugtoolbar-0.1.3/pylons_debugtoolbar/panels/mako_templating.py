from paste.deploy.converters import asbool
import pylons
from webhelpers.html import literal
from mako.runtime import TemplateNamespace
from pylons_debugtoolbar.panels import DebugPanel
from pylons_debugtoolbar.utils import format_template_fname
from pylons_debugtoolbar.utils import get_template_inherits


class MakoDebugPanel(DebugPanel):
    """Panel that displays mako template vars and its inherits."""
    name = 'Mako'
    has_content = True
    result = {}

    def __init__(self, request, config):
        self.config = config
        if asbool(config.get('pdtb.panel_mako', True)):
            self.is_active = True

    def nav_title(self):
        num = len(self.result['tmpl_vars'])
        return literal('Mako <span class="title-grey">(%d)</span>' % num)

    def nav_subtitle(self):
        return self.result['tmpl_name']

    def title(self):
        if self.result['tmpl_name']:
            tmpl_text = ": %s" % self.result['tmpl_name']
        else:
            tmpl_text = ""
        return 'Mako%s' % tmpl_text

    def content(self):
        if not self.result:
            if pylons.__version__.startswith('0'):
                c = pylons.c
                new_pylons = False
            else:
                c = pylons.tmpl_context
                new_pylons = True

            self.result = {
                'global_keys': [],
                'tmpl_vars': [],
                'tmpl_name': '',
                'tmpl_inherits': [],
            }
            tmpl_obj = getattr(c, '__template_object', None)
            if tmpl_obj and isinstance(tmpl_obj, TemplateNamespace):
                self.result['tmpl_name'] = format_template_fname(tmpl_obj.uri)
                self.result['tmpl_inherits'] = get_template_inherits(tmpl_obj)
                self.result['tmpl_inherits'].reverse()
                self.result['tmpl_inherits'].append(self.result['tmpl_name'])
            if getattr(c, '__tmpl_vars', None):
                global_keys = [
                    'local', 'translator', 'session', 'response', '_',
                    'capture', 'c', 'url', 'h', 'self', 'caller', 'request',
                    'next', 'N_', 'ungettext', 'config',
                ]
                if new_pylons:
                    global_keys.extend(['tmpl_context', 'app_globals'])
                else:
                    global_keys.append('g')
                self.result['global_keys'] = sorted(global_keys)

                system_keys = [
                    '__class__', '__delattr__', '__dict__', '__doc__',
                    '__format__', '__getattribute__', '__hash__', '__init__',
                    '__module__', '__new__', '__reduce__', '__reduce_ex__',
                    '__repr__', '__setattr__', '__sizeof__', '__str__',
                    '__subclasshook__', '__tmpl_vars', '__weakref__',
                    '____local__', '____name__', '__call__', '__contains__',
                    '__delitem__', '__dir__', '__getattr__', '__getitem__',
                    '__iter__', '__len__', '__nonzero__', '__setitem__',
                    '_current_obj', '_current_obj_orig', '_object_stack',
                    '_current_obj_restoration', '_pop_object',
                    '_pop_object_orig', '_pop_object_restoration',
                    '_push_object', '_push_object_orig',
                    '_push_object_restoration', '__template_object',
                ]
                if self.config.get('pdtb.mako_c_exclude'):
                    ex = self.config['pdtb.mako_c_exclude']
                    excluded_keys = [k for k in ex.strip().split() if k]
                    system_keys.extend(excluded_keys)

                all_c_keys = dir(c)
                c_keys = filter(lambda x: x not in system_keys, all_c_keys)

                c_attrs = [("c.%s" % k, getattr(c, k)) for k in c_keys]
                tmpl_vars = sorted(getattr(c,'__tmpl_vars'), key=lambda x:x[0])
                self.result['tmpl_vars'] = c_attrs + tmpl_vars

        vars = {'result': self.result}
        return self.render('/panels/templates/mako.mako', **vars)
