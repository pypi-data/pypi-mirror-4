from __future__ import with_statement

import datetime
import json
import logging

from random import random
from time import time
from contextlib import contextmanager

from webob import Request

# Actually import time, but close enough to
# wsgi process start time to use as such
PROCESS_START_TIME = datetime.datetime.utcnow()

log = logging.getLogger(__name__)


def uptime():
    """Return process uptime (in seconds) for this wsgi app."""
    td = datetime.datetime.utcnow() - PROCESS_START_TIME
    return (td.days * 3600 * 24) + td.seconds


class StatsRecord(object):
    def __init__(self, request):
        self._custom_stats = {}
        self.timers = {}
        self.url = request.environ['PATH_INFO']
        if request.environ['QUERY_STRING']:
            self.url += '?' + request.environ['QUERY_STRING']
        self.request = request
        # Avoid double-timing things
        self._now_timing = set()

    def add(self, k, v):
        self._custom_stats[k] = v

    def remove(self, k):
        if k in self._custom_stats:
            del self._custom_stats[k]

    def __repr__(self):
        stats = dict(
            url=self.url,
            uptime=uptime(),
            timings=dict((k, int(v * 1000))
                         for k, v in self.timers.iteritems())
        )
        stats.update(self._custom_stats)
        return self.to_string(stats)

    def to_string(self, stats):
        return json.dumps(stats)

    @contextmanager
    def timing(self, name):
        if name not in self._now_timing:
            self._now_timing.add(name)
            self.timers.setdefault(name, 0)
            begin = time()
            try:
                yield True
            finally:
                end = time()
                self.timers[name] += end-begin
                self._now_timing.remove(name)
        else:
            yield False


class Timer(object):
    '''Decorator to time a method call'''
    def __init__(self, timer_name, target_class, *names, **kw):
        self.timer_name = timer_name
        self.target_class = target_class
        self.names = names
        self.debug_each_call = kw.get('debug_each_call', True)

    def decorate(self, middleware):
        for name in self.names:
            setattr(self.target_class, name,
                    TimingDecorator(self.target_class.__dict__[name],
                                    self.timer_name,
                                    name,
                                    self.debug_each_call,
                                    middleware))


class TimingDecorator(object):
    def __init__(self, inner, timer_name, method_name, debug_each_call, middleware):
        self._inner = inner
        self.timer_name = timer_name
        self.method_name = method_name
        self.debug_each_call = debug_each_call and \
                               log.isEnabledFor(logging.DEBUG)
        self.middleware = middleware

    def __get__(self, inst, cls=None):
        func = self._inner.__get__(inst, cls)

        def wrapper(*args, **kwargs):
            return self.run_and_log(func, inst, *args, **kwargs)
        return wrapper

    def __call__(self, *args, **kwargs):
        return self.run_and_log(self._inner, None, *args, **kwargs)

    def run_and_log(self, func, instance, *args, **kwargs):
        stats = self.middleware.stat_record
        if not stats:
            return func(*args, **kwargs)

        timer_name = self.timer_name.format(
            method_name=self.method_name,
            instance=instance,
        )
        with stats.timing(timer_name) as timed_this_one:
            if self.debug_each_call and timed_this_one:
                call_method = '%s call: ' % timer_name
                if instance:
                    call_method += str(type(instance))
                call_method += ' ' + self.method_name
                call_args = ' args=%s kwargs=%s' % (args, kwargs)
                if len(call_args) > 100:
                    call_args = call_args[:100] + '...'
                log.debug(call_method + call_args)
            return func(*args, **kwargs)


class TimerMiddleware(object):
    stat_record_class = StatsRecord

    def __init__(self, app, config):
        self.app = app
        self.config = config
        self.log = logging.getLogger('stats')
        self.sample_rate = float(self.config.get('stats.sample_rate', 0))
        self.stat_record = None
        if self.sample_rate:
            for t in self.timers():
                t.decorate(self)

    def __call__(self, environ, start_response):
        req = Request(environ)
        active = random() < self.sample_rate

        if active:
            self.stat_record = s = self.stat_record_class(req)
            with s.timing('total'):
                resp = req.get_response(self.app)
                result = resp(environ, start_response)
                s = self.before_logging(s)
            self.log.info('%r', s)
            self.stat_record = None
        else:
            resp = req.get_response(self.app)
            result = resp(environ, start_response)

        return result

    def before_logging(self, stat_record):
        """Called right before the timing results are logged. Override in a
        sublass if you want to modify the stat_record before it's logged.
        """
        return stat_record

    def timers(self):
        """Return a list of :class:`Timer` objects. Override in a subclass."""
        return []
