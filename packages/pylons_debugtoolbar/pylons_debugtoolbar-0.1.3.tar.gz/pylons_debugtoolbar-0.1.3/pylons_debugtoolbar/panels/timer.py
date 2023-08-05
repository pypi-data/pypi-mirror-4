import resource
import time
from paste.deploy.converters import asbool
from pylons_debugtoolbar.panels import DebugPanel


class TimerDebugPanel(DebugPanel):
    """Panel that displays the time a response took in milliseconds."""
    name = 'Timer'
    has_content = True
    has_resource = True

    def __init__(self, request, config):
        self.request = request
        if asbool(config.get('pdtb.panel_timer', True)):
            self.is_active = True

    def __enter__(self):
        self._start_time = time.time()
        if self.has_resource:
            self._start_rusage = resource.getrusage(resource.RUSAGE_SELF)

    def process_response(self, response):
        self.stats = {'total_time': (time.time() - self._start_time) * 1000}
        self._end_rusage = resource.getrusage(resource.RUSAGE_SELF)
        self.stats['utime'] = 1000 * self._elapsed_ru('ru_utime')
        self.stats['stime'] = 1000 * self._elapsed_ru('ru_stime')
        self.stats['total'] = self.stats['utime'] + self.stats['stime']
        self.stats['minflt'] = self._elapsed_ru('ru_minflt')
        self.stats['majflt'] = self._elapsed_ru('ru_majflt')

    def nav_title(self):
        return 'Time'

    def nav_subtitle(self):
        utime = self._end_rusage.ru_utime - self._start_rusage.ru_utime
        stime = self._end_rusage.ru_stime - self._start_rusage.ru_stime
        return 'CPU: %(cum)0.2fms (%(total)0.2fms)' % dict(
            cum=(utime + stime) * 1000.0,
            total=self.stats['total_time'],
        )

    def title(self):
        return 'Time'

    def _elapsed_ru(self, name):
        return (
            getattr(self._end_rusage, name) -
            getattr(self._start_rusage, name)
        )

    def content(self):
        rows = (
            ('User CPU time', '%(utime)0.3f msec' % self.stats),
            ('System CPU time', '%(stime)0.3f msec' % self.stats),
            ('Total CPU time', '%(total)0.3f msec' % self.stats),
            ('Elapsed time', '%(total_time)0.3f msec' % self.stats),
        )
        return self.render('/panels/templates/timer.mako', rows=rows)
