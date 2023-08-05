import sys
import pkg_resources
from operator import itemgetter
import platform
from paste.deploy.converters import asbool
from webhelpers.html import literal

from pylons_debugtoolbar.panels import DebugPanel


plat = 'Python %s on %s' % (sys.version, platform.platform())

packages = []
for distribution in pkg_resources.working_set:
    name = distribution.project_name
    packages.append({
        'version': distribution.version,
        'lowername': name.lower(),
        'name': name,
    })

packages = sorted(packages, key=itemgetter('lowername'))


class VersionDebugPanel(DebugPanel):
    """Panel that displays the Python version, the Pylons version, and the
    versions of other software on your PYTHONPATH.
    """
    name = 'Version'
    has_content = True

    def __init__(self, request, config):
        self.config = config
        if asbool(config.get('pdtb.panel_versions', True)):
            self.is_active = True

    def nav_title(self):
        if self.config.get('version'):
            version_html = (
                '<span class="title-grey">(%s)</span>' %
                self.config['version'].split()[0]
            )
        else:
            version_html = ""
        return literal('Versions %s' % version_html)

    def nav_subtitle(self):
        return ''

    def title(self):
        return 'Versions'

    def content(self):
        vars = {
            'platform': plat,
            'packages': packages,
            'project_version': self.config.get('version'),
        }
        return self.render('/panels/templates/versions.mako', **vars)
