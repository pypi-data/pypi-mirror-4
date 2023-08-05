import time
from functools import wraps
import threading
from paste.deploy.converters import asbool
from pylons_debugtoolbar.panels import DebugPanel
from pylons_debugtoolbar.panels.cache_base import Calls, _get_calls
from pylons_debugtoolbar.panels.cache_base import repr_value
from pylons_debugtoolbar.panels.cache_base import get_nav_subtitle
from pylons_debugtoolbar.panels.cache_base import get_content
import logging


logger = logging.getLogger(__name__)
instance = threading.local()


class MemcachedCalls(Calls):
    pass


def get_calls():
    return _get_calls(instance, MemcachedCalls)


def record(func):
    @wraps(func)
    def recorder(*args, **kwargs):
        call = {
            'function': func.__name__,
            'args': None,
        }
        get_calls().append(call)
        call['args'] = repr_value(args[1:])
        ret = None
        try:
            call['start'] = time.time()
            ret = func(*args, **kwargs)
        finally:
            call['duration'] = (time.time() - call['start']) * 1000
            if func.__name__.startswith('get'):
                if ret is None:
                    call['miss'] = 1
                else:
                    call['hit'] = 1

        call['ret'] = repr_value(ret)
        return ret
    return recorder


try:
    import memcache as memc


    class TrackingMemcacheClient(memc.Client):

        @record
        def flush_all(self, *args, **kwargs):
            return origClient.flush_all(self, *args, **kwargs)

        @record
        def delete_multi(self, *args, **kwargs):
            return origClient.delete_multi(self, *args, **kwargs)

        @record
        def delete(self, *args, **kwargs):
            return origClient.delete(self, *args, **kwargs)

        @record
        def incr(self, *args, **kwargs):
            return origClient.incr(self, *args, **kwargs)

        @record
        def decr(self, *args, **kwargs):
            return origClient.decr(self, *args, **kwargs)

        @record
        def add(self, *args, **kwargs):
            return origClient.add(self, *args, **kwargs)

        @record
        def append(self, *args, **kwargs):
            return origClient.append(self, *args, **kwargs)

        @record
        def prepend(self, *args, **kwargs):
            return origClient.prepend(self, *args, **kwargs)

        @record
        def replace(self, *args, **kwargs):
            return origClient.replace(self, *args, **kwargs)

        @record
        def set(self, *args, **kwargs):
            return origClient.set(self, *args, **kwargs)

        @record
        def cas(self, *args, **kwargs):
            return origClient.cas(self, *args, **kwargs)

        @record
        def set_multi(self, *args, **kwargs):
            return origClient.set_multi(self, *args, **kwargs)

        @record
        def get(self, *args, **kwargs):
            return origClient.get(self, *args, **kwargs)

        @record
        def gets(self, *args, **kwargs):
            return origClient.gets(self, *args, **kwargs)

        @record
        def get_multi(self, *args, **kwargs):
            return origClient.get_multi(self, *args, **kwargs)

    # NOTE issubclass is true of both are the same class
    if not issubclass(memc.Client, TrackingMemcacheClient):
        logger.debug('installing memcache.Client with tracking')
        origClient = memc.Client
        memc.Client = TrackingMemcacheClient

except ImportError:
    logger.exception('unable to install memcache.Client with tracking')


class MemcachedDebugPanel(DebugPanel):
    name = 'Memcached'
    has_content = True

    def __init__(self, request, config):
        self.config = config
        if asbool(config.get('pdtb.panel_memcached', True)):
            self.is_active = True

    def __enter__(self):
        get_calls().reset()

    def nav_title(self):
        return 'Memcached'

    def title(self):
        return 'Memcached calls'

    def nav_subtitle(self):
        calls = get_calls().calls()
        return get_nav_subtitle(calls)

    def content(self):
        max_result_len = int(self.config.get('pdtb.cache_result_max_len', 100))
        calls = get_calls().calls()
        vars = get_content(calls, max_result_len)
        return self.render('/panels/templates/memcached.mako', **vars)
