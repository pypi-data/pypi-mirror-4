from pylons_debugtoolbar.utils import render_mako


class DebugPanel(object):
    """Base class for debug panels."""
    name = 'BasePanel'
    has_content = False # If content returns something, set to true in subclass

    # If the client is able to activate/de-activate the panel
    user_activate = False

    # Default to is_active = False
    is_active = False

    # Panel methods
    def dom_id(self):
        return 'id_%s' % self.name

    def nav_title(self):
        """Title showing in toolbar"""
        raise NotImplementedError

    def nav_subtitle(self):
        """Subtitle showing until title in toolbar"""
        return ''

    def title(self):
        """Title showing in panel"""
        raise NotImplementedError

    def content(self):
        raise NotImplementedError

    def process_request(self):
        pass

    def process_response(self, response):
        pass

    def render(self, template_uri, **vars):
        return render_mako(template_uri, **vars)

    def __enter__(self):
        pass

    def __exit__(self, *exc_info):
        pass
