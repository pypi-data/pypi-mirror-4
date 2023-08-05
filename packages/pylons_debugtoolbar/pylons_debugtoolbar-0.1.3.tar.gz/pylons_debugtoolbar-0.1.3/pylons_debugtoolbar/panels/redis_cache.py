import time
import logging
import threading
from paste.deploy.converters import asbool
from pylons_debugtoolbar.panels import DebugPanel
from pylons_debugtoolbar.panels.cache_base import Calls, _get_calls
from pylons_debugtoolbar.panels.cache_base import repr_value
from pylons_debugtoolbar.panels.cache_base import get_nav_subtitle
from pylons_debugtoolbar.panels.cache_base import get_content


logger = logging.getLogger(__name__)
instance = threading.local()

READ_METHODS = (
    'LLEN', 'LRANGE', 'LINDEX', 'LPOP', 'RPOP', 'RPOPLPUSH', 'SCARD',
    'SINTER', 'SUNION', 'SDIFF', 'SMEMBERS', 'SRANDMEMBER', 'ZRANK',
    'ZREVRANK', 'ZRANGE', 'ZREVRANGE', 'ZRANGEBYSCORE', 'ZCARD', 'ZSCORE',
    'HLEN', 'HKEYS', 'HVALS', 'HGETALL', 'LASTSAVE',
)


class RedisCalls(Calls):
    pass


def get_calls():
    return _get_calls(instance, RedisCalls)


try:
    import redis


    class TrackingRedis(redis.Redis):
        def execute_command(self, func_name, *args, **kwargs):
            call = {
                'function': func_name.lower(),
                'args': repr_value(args),
            }
            ret = None
            try:
                call['start'] = time.time()
                ret = origRedis.execute_command(
                    self, func_name, *args, **kwargs
                )
            finally:
                call['duration'] = (time.time() - call['start']) * 1000
                if func_name in READ_METHODS:
                    if ret:
                        call['hit'] = 1
                    else:
                        call['miss'] = 1

            call['ret'] = repr_value(ret)
            get_calls().append(call)
            return ret

    # NOTE issubclass is true if both are the same class
    if not issubclass(redis.Redis, TrackingRedis):
        logger.debug('installing redis.client.Redis with tracking')
        origRedis = redis.Redis
        redis.Redis = TrackingRedis

except ImportError:
    logger.exception('unable to install redis.client.Redis with tracking')


class RedisDebugPanel(DebugPanel):
    name = 'Redis'
    has_content = True

    def __init__(self, request, config):
        self.config = config
        if asbool(config.get('pdtb.panel_redis', True)):
            self.is_active = True

    def __enter__(self):
        get_calls().reset()

    def nav_title(self):
        return 'Redis'

    def title(self):
        return 'Redis calls'

    def nav_subtitle(self):
        calls = get_calls().calls()
        return get_nav_subtitle(calls)

    def content(self):
        max_result_len = int(self.config.get('pdtb.cache_result_max_len', 100))
        calls = get_calls().calls()
        vars = get_content(calls, max_result_len)
        return self.render('/panels/templates/memcached.mako', **vars)
