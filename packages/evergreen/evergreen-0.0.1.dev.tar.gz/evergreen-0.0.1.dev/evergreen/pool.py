#
# This file is part of Evergreen. See the NOTICE for more information.
#

import evergreen
from evergreen.event import Event
from evergreen.locks import Semaphore

__all__ = ['Pool']


class Pool(object):

    def __init__(self, size=1000):
        self._size = size
        self._lock = Semaphore(size)
        self._running_jobs = 0
        self._end_event = Event()
        self._end_event.set()

    def spawn(self, func, *args, **kw):
        self._lock.acquire()
        self._running_jobs += 1
        self._end_event.clear()
        return evergreen.spawn(self._runner, func, args, kw)

    def join(self, timeout=None):
        return self._end_event.wait(timeout)

    def _runner(self, func, args, kw):
        try:
            func(*args, **kw)
        finally:
            self._running_jobs -= 1
            if self._running_jobs == 0:
                self._end_event.set()
            self._lock.release()

    def __repr__(self):
        return '<%s(size=%d), %d running jobs>' % (self.__class__.__name__, self._size, self._running_jobs)

