from operator import itemgetter

from paste.deploy.converters import asbool
from pylons_debugtoolbar.panels import DebugPanel


class SettingsDebugPanel(DebugPanel):
    """A panel to display Pyramid deployment settings for your application
    (the values in ``pylons.config``).
    """
    name = 'Settings'
    has_content = True

    def __init__(self, request, config):
        self.config = config
        if asbool(config.get('pdtb.panel_settings', True)):
            self.is_active = True

    def nav_title(self):
        return 'Settings'

    def title(self):
        return 'Settings'

    def content(self):
        reprs = [(k, repr(v)) for k, v in self.config.iteritems()]
        self.settings = sorted(reprs, key=itemgetter(0))
        vars = {'settings': self.settings, 'asbool': asbool}
        return self.render('/panels/templates/settings.mako', **vars)
