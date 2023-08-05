from paste.deploy.converters import asbool
from webhelpers.html import literal
from pylons_debugtoolbar.panels import DebugPanel


class RoutesDebugPanel(DebugPanel):
    """A panel to display the routes used by your Pylons application."""
    name = 'Routes'
    has_content = True

    def __init__(self, request, config):
        if asbool(config.get('pdtb.panel_routes', True)):
            self.is_active = True
        self.mapper = config['routes.map']
        if self.mapper is None:
            self.has_content = False
            self.is_active = False

    def nav_title(self):
        return literal(
            'Routes <span class="title-grey">(%d)</span>' %
            len(self.mapper.matchlist)
        )

    def title(self):
        return 'Routes'

    def content(self):
        if self.mapper is not None:
            routes = self.mapper.matchlist
            result = []
            for route in routes:
                result.append(dict(
                    route=route.routepath,
                    name=route.name or '',
                    requirements=route.reqs,
                    controller=route.defaults.get('controller'),
                    action=route.defaults.get('action', ''),
                    defaults=route.defaults,
                ))
            return self.render('/panels/templates/routes.mako', result=result)
        return ''
