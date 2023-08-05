from pylons_debugtoolbar.utils import replace_insensitive
from pylons_debugtoolbar.utils import render_mako

from pylons_debugtoolbar.panels.logger import LoggingPanel
from pylons_debugtoolbar.panels.mako_templating import MakoDebugPanel
from pylons_debugtoolbar.panels.request import RequestDebugPanel
from pylons_debugtoolbar.panels.routes import RoutesDebugPanel
from pylons_debugtoolbar.panels.settings import SettingsDebugPanel
from pylons_debugtoolbar.panels.sqla import SQLAlchemyDebugPanel
from pylons_debugtoolbar.panels.versions import VersionDebugPanel
from pylons_debugtoolbar.panels.timer import TimerDebugPanel
from pylons_debugtoolbar.panels.memcached_cache import MemcachedDebugPanel
from pylons_debugtoolbar.panels.redis_cache import RedisDebugPanel


panel_classes = (
    VersionDebugPanel,
    SettingsDebugPanel,
    RequestDebugPanel,
    RoutesDebugPanel,
    LoggingPanel,
    TimerDebugPanel,
    MakoDebugPanel,
    SQLAlchemyDebugPanel,
    MemcachedDebugPanel,
    RedisDebugPanel,
)


class DebugToolbar(object):

    html_types = ('text/html', 'application/xml+html')

    def __init__(self, request, config):
        self.request = request
        self.config = config
        self.panels = []
        for panel_class in panel_classes:
            panel_inst = panel_class(request, config)
            if panel_inst.is_active:
                self.panels.append(panel_inst)

    def process_response(self, response):
        # If the body in HTML, then we add the toolbar to the response.
        if self.panels:
            for panel in self.panels:
                panel.process_response(response)

            if response.content_type in self.html_types:
                vars = {
                    'panels': self.panels,
                    'button_style': '',
                }

                toolbar_html = render_mako('/templates/toolbar.mako', **vars)
                response_html = response.body
                toolbar_html = toolbar_html.encode(response.charset or 'utf-8')
                body = replace_insensitive(
                    response_html,
                    '</body>',
                    toolbar_html + '</body>'
                )
                response.app_iter = [body]
                response.content_length = len(body)
