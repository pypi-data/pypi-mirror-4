from pprint import saferepr
from copy import deepcopy
from paste.deploy.converters import asbool
from pylons_debugtoolbar.panels import DebugPanel


class RequestDebugPanel(DebugPanel):
    """A panel to display request variables (controller, action, route info,
    POST/GET, session, cookies, request headers, response headers and ad-hoc
    request attributes).
    """
    name = 'Request'
    has_content = True

    def __init__(self, request, config):
        self.request = request
        if asbool(config.get('pdtb.panel_request', True)):
            self.is_active = True

    def process_response(self, response):
        self.request_headers = [
            (k, v) for k, v in sorted(self.request.headers.items())
        ]
        self.response_headers = [
            (k, v) for k, v in sorted(response.headerlist)
        ]

    def nav_title(self):
        return 'Request'

    def title(self):
        return 'Request'

    def content(self):
        vars = {}
        attr_dict = self.request.__dict__.copy()
        # environ is displayed separately
        del attr_dict['environ']
        if 'response' in attr_dict:
            attr_dict['response'] = repr(attr_dict['response'])
        defaults = deepcopy(self.request.environ['routes.route'].defaults)
        controller_vars = [
            ('controller', defaults.pop('controller', 'unknown...')),
            ('action', defaults.pop('action', 'unknown...')),
        ]
        controller_vars.extend([(k, v) for k, v in defaults.iteritems()])
        route_vars = [
            ('Pattern', self.request.environ['routes.route'].routepath),
            ('Name', self.request.environ['routes.route'].name),
            ('Requirements', self.request.environ['routes.route'].reqs),
        ]
        env = dict(self.request.environ.items())
        if 'webob.adhoc_attrs' in env:
            del env['webob.adhoc_attrs']
        vars.update({
            'controller_vars': controller_vars,
            'route_vars': route_vars,
            'get': [(k, self.request.GET.getall(k)) for k in self.request.GET],
            'post': [(k, [saferepr(p) for p in self.request.POST.getall(k)])
                    for k in self.request.POST],
            'cookies': [
                (k, self.request.cookies.get(k)) for k in self.request.cookies
            ],
            'attrs': attr_dict,
            'environ': env,
            'request_headers': self.request_headers,
            'response_headers': self.response_headers,
        })

        if hasattr(self.request, 'session'):
            vars.update({
                'session': self.request.session,
            })

        return self.render('/panels/templates/request.mako', **vars)
