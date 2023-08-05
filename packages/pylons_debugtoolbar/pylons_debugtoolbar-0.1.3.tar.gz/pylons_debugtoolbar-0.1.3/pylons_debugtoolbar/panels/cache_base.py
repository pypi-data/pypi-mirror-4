import cPickle as pickle
import pprint
import logging
import traceback


logger = logging.getLogger(__name__)


class Calls(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self._calls = []

    def append(self, call):
        self._calls.append(call)

    def calls(self):
        return self._calls

    def size(self):
        return len(self._calls)

    def last(self):
        return self._calls[-1]


def _get_calls(instance, calls_cls):
    if not hasattr(instance, 'calls'):
        instance.calls = calls_cls()
    return instance.calls


def repr_value(ret):
    try:
        if isinstance(ret, dict):
            out = ret.copy()
            pickle_ = out.pop('__pickle__', None)
            if pickle_:
                out.update(pickle.loads(pickle_))
        elif isinstance(ret, (list, tuple)) and len(ret) == 1:
            out, = ret
        else:
            out = ret
    except Exception, e:
        try:
            out = 'Unable to parse: %r because: %r' % (ret, e)
        except Exception:
            out = 'Unable to parse'

    out = pprint.pformat(out, indent=False, width=50)
    out = ' '.join(out.split())

    if out[100:]:
        return out
    else:
        return out[:100]


def get_nav_subtitle(calls):
    duration = sum([call['duration'] for call in calls])
    n = len(calls)
    if n > 0:
        return '%d calls (%0.2fms)' % (n, duration)
    else:
        return '0 calls'


def get_content(calls, result_max_len):
    stats = dict(
        calls=0,
        duration=0,
        hits=0,
        misses=0,
    )
    commands = dict()

    try:
        for call in calls:
            if len(call['ret']) > result_max_len:
                call['ret'] = "%s..." % call['ret'][:result_max_len]
            stats['calls'] += 1
            stats['duration'] += call['duration']
            stats['hits'] += call.get('hit', 0)
            stats['misses'] += call.get('miss', 0)
            function = call['function']
            commands[function] = commands.get(function, 0) + 1

        calls = sorted(calls, key=lambda c: c['start'])

        if stats['misses'] and stats['hits']:
            stats['hitratio'] = 100. / stats['hits'] / stats['misses']
        elif stats['misses']:
            stats['hitratio'] = 0
        else:
            stats['hitratio'] = 100.

        return {
            'calls': calls,
            'stats': stats,
            'commands': commands,
        }
    except Exception:
        traceback.print_exc()
