#!/usr/bin/env python

from __future__ import absolute_import
import collections
from datetime import timedelta
import inspect 
import logging
import sys
from time import time

class StackFrame(collections.namedtuple('Stack', ('frame, filename, line, method, source, x'))):
    def __repr__(self):
        return 'File "%s", line %d in %s' % (self.filename, self.line, self.method)

def CallerStackFrame(depth=1):
    stack = inspect.stack()
    if len(stack) < depth+1:
        return "Unknown"
    return StackFrame._make(stack[-depth])

class Error(Exception): pass
class TimerFinishedError(Error): pass

class _FinishedTimer:
    def __call__(self, *_):
        raise TimerFinishedError(self.how)

class Timer:

    logger = logging.getLogger(__name__)
    debug = logger.debug
    warning = logger.warning

    @staticmethod
    def _normalize_time(time_limit):
        if isinstance(time_limit, timedelta):
            return time_limit.total_seconds()
        return time_limit

    def __init__(self, time_limit=None, comment=''):
        self.limit = time_limit
        self.time_limit = self._normalize_time(time_limit)
        self.start_time = time()
        self.last_time = self.start_time
        self.caller = CallerStackFrame()
        if comment:
            comment = ', ' + comment
        self.debug("%s%s: start timer" % (self.caller, comment))

    def __enter__(self):
        return self

    def done(self):
        self(time_limit=-1, comment="DONE")
        self.__class__ = _FinishedTimer
        self.how = "This timer is shut down because its done method was already called"

    def __exit__(self, *args):
        self(time_limit=-1, comment="EXITING")
        self.__class__ = _FinishedTimer
        self.how = "This timer is shut down because its __exit__ method was already called"

    def __del__(self):
        try:
            self(time_limit=-1, comment="GARBAGE COLLECTED")
        except: 
            pass

    @staticmethod
    def pretty_print_time(t):
        return "%s microseconds" % format(int(t * 1000000), ",d")

    def __call__(self, time_limit=None, comment=''):
        log = self.debug
        if comment:
            comment = ', ' + comment 
        if time_limit is not None and self._normalize_time(time_limit) < self.last_time:
            log = self.warning
        now = time()
        log("%s, from %s%s: %s, %s" % (CallerStackFrame(), self.caller, comment, self.pretty_print_time(now - self.last_time), self.pretty_print_time(now - self.start_time)))
        self.last_time = now



        


        
        
        
        

