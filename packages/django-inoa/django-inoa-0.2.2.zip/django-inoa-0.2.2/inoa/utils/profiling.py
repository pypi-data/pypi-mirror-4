# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import connection
import logging
import threading
import time


"""
A collection of tools for simple profiling of blocks of code, entire methods or requests.
Measures elapsed time and queries performed within the block,
and outputs to the Django built-in logging system.
Messages are issued to the 'profiling' logger with the Debug level.

Logging is disabled when DEBUG = False, unless the following entry is added to the project settings:
ENABLE_PROFILER_IN_PRODUCTION = True

If you want to send the profiler output to stdout, define a suitable logger/handler combination
in your project settings. A minimal setup would be:

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'profiling': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}

"""

profiler_enabled = settings.DEBUG or getattr(settings, 'ENABLE_PROFILER_IN_PRODUCTION', False)
bolt_easter_egg = getattr(settings, 'PROFILER_BOLT_EASTER_EGG', False)
logger = logging.getLogger('profiling')

def method_profiler(method):
    """
    Use as a decorator in any method. Usage:
    
    @method_profiler
    def my_method(arg1, arg2):
        ... # Do stuff you want to benchmark.
    """
    if not profiler_enabled:
        return method
    def wrapper(*args, **kwargs):
        p = Profiler("%s.%s" % (method.__module__, method.__name__))
        ret = method(*args, **kwargs)
        p.stop()
        return ret
    wrapper.__name = method.__name__
    wrapper.__module__ = method.__module__
    return wrapper


class ProfilerMiddleware(object):
    """
    A middleware which ouputs time spent and query count for every request handled by Django.
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        request._profiler_middleware_profiler = Profiler("%s.%s" % (view_func.__module__, view_func.__name__))
    def process_response(self, request, response):
        profiler = getattr(request, '_profiler_middleware_profiler', None)
        if profiler:
            profiler.stop()
        return response


class Profiler(object):
    """
    Allows profiling of sections of code within a method. Usage:
    
    def my_method(arg1, arg2):
        ... # Do stuff you don't care about.
        profiler = Profiler()                 # Begins profiling. Note: accepts an optional name parameter.
        ... # Do stuff you want to benchmark separately.
        profiler.checkpoint()                 # Outputs partial time and queries.
        ... # Do more stuff you want to benchmark separately.
        profiler.checkpoint('Foo'd the bar')  # Outputs partial time and queries.
        ... # Do a little bit more of stuff.
        profiler.stop()                       # Outputs total time and queries.
        ... # Do stuff you don't care about.
    
    You can obtain a reference to the latest instantiated profiler with Profiler.get_latest().
    It creates a new profiler automatically if none exists. This is method is thread-safe.
    """
    local_store = threading.local()

    @classmethod
    def get_latest(cls):
        return getattr(cls.local_store, 'latest_instance', cls())

    def __init__(self, name=None):
        self.name = name or ("profiler %s" % id(self))
        self.start()

    def start(self):
        if not profiler_enabled:
            return
        self.t0 = time.time()
        self.q0 = len(connection.queries) #@UndefinedVariable
        self.t1, self.q1 = self.t0, self.q0
        self.count = 0
        self.__class__.latest_instance = self

    def checkpoint(self, name=None):
        if not profiler_enabled:
            return
        t2 = time.time()
        q2 = len(connection.queries) #@UndefinedVariable
        self.count += 1
        name = name or self.count
        if bolt_easter_egg:
            logger.debug("Bolt would have run %.01f meters during partial %s, with %s queries." % ((t2 - self.t1)*10.4389, name, q2 - self.q1))
        else:
            logger.debug("Partial %s in %.04f seconds with %s queries." % (name, t2 - self.t1, q2 - self.q1))
        self.t1, self.q1 = t2, q2
        self.__class__.latest_instance = self

    def stop(self):
        if not profiler_enabled:
            return
        t2 = time.time()
        q2 = len(connection.queries) #@UndefinedVariable
        if bolt_easter_egg:
            logger.debug("Bolt would have run %.01f meters during execution of %s, with %s queries." % ((t2 - self.t0)*10.4389, self.name, q2 - self.q0))
        else:
            logger.debug("Executed %s in %.04f seconds with %s queries." % (self.name, t2 - self.t0, q2 - self.q0))
