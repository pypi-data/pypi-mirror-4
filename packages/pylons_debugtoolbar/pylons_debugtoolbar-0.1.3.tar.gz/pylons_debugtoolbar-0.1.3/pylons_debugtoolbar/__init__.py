from contextlib import nested
import os
from paste.deploy.converters import asbool
from webob import Request, Response
from pylons_debugtoolbar.toolbar import DebugToolbar


root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_path=[os.path.join(root, 'templates')]


class DebugToolbarMiddleware(object):
    def __init__(self, app, config=None):
        self.app = app
        self.config = config

    def __call__(self, environ, start_response):
        if not asbool(self.config.get('pdtb.enabled', True)):
            return self.app(environ, start_response)

        request = Request(environ)
        debug_toolbar = DebugToolbar(request, self.config)

        meta = []
        def hook(status, headers, exc_info=None):
            meta[:] = [status, headers, exc_info]

        processors = [cls for cls in debug_toolbar.panels]
        with nested(*processors):
            iterable = self.app(environ, hook)
            content = ''.join(iterable)
            if hasattr(iterable, 'close'):
                iterable.close()

        status, headers, exc_info = meta
        if exc_info:
            start_response(status, headers, exc_info)
            return [content]

        response = Response(content, status, headers)
        debug_toolbar.process_response(response)

        return response(environ, start_response)
