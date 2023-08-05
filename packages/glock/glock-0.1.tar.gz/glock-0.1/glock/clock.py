# Copyright 2012 Johan Rydberg.
# Copyright 2001-2008 Twisted Matrix Laboratories.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Simple abstraction of a clock that allows callers to read out the
current time, but also schedule future calls.  Scheduled calls can be
cancelled and resetted.

The MockClock and DelayedCall classes and their functionality is based
on the twisted.internet.task.Clock class from Twisted which is
released under a MIT license.
"""

from time import time as _time

from gevent.event import Event
from gevent import spawn_later, kill as gevent_kill, sleep as gevent_sleep
import gevent


class AlreadyCancelled(Exception):
    pass


class AlreadyCalled(Exception):
    pass


class DelayedCall(object):
    """Representation of a call in the future.

    @ivar resetter: Function that schedules the passed delayed call
        for dispatch.  If the delayed call has already been scheduled,
        it will first be canceler.

    @ivar canceler: Function that cancels a scheduled delayed call.
    """

    cancelled = 0
    called = 0

    def __init__(self, clock, time, func, args, kw, cancel, reset):
        self.clock = clock
        self._time, self.func, self.args, self.kw = time, func, args, kw
        self.resetter = reset
        self.canceler = cancel

    def __call__(self):
        if self.called:
            raise AlreadyCalled()
        self.called = 1
        self.func(*self.args, **self.kw)

    @property
    def time(self):
        return self._time

    def cancel(self):
        """Unschedule this call.

        @raise AlreadyCancelled: Raised if this call has been cancelled.
        @raise AlreadyCalled: Raised if this call has already been made.

        """
        if self.cancelled:
            raise AlreadyCancelled()
        elif self.called:
            raise AlreadyCalled()
        else:
            self.canceler(self)
            self.cancelled = 1
            if self.debug:
                self._str = str(self)
            del self.func, self.args, self.kw

    def reset(self, seconds_from_now):
        """Reschedule this call for a different time.

        @param seconds_from_now: The number of seconds from the time
            of the reset call at which this call will be scheduled.

        @raise AlreadyCancelled: Raised if this call has been cancelled.
        @raise AlreadyCalled: Raised if this call has already been made.
        """
        if self.cancelled:
            raise AlreadyCancelled()
        elif self.called:
            raise AlreadyCalled()
        else:
            new_time = self.clock.time() + seconds_from_now
            self._time = new_time
            self.resetter(self)

    def __le__(self, other):
        return self._time <= other.time


class Clock(object):
    """Abstraction of a clock that has functionality for reporting
    current time and scheduler functions to be called in the future.
    """

    def __init__(self):
        self._greenlets = {}

    def _call(self, dc):
        del self._greenlets[dc]
        dc()

    def _canceler(self, dc):
        if dc in self._greenlets:
            self._greenlets.pop(dc).kill()

    def _resetter(self, dc):
        """Schedule or reschedule delayed dc."""
        self._canceler(dc)
        self._greenlets[dc] = spawn_later(
            dc.time - self.time(), self._call, dc)

    def sleep(self, seconds=0):
        """Sleep for C{seconds}."""
        gevent_sleep(seconds)

    advance = sleep

    def call_later(self, seconds, fn, *args, **kw):
        """Call function C{fn} at a later time."""
        dc = DelayedCall(self, self.time() + seconds,
            fn, args, kw, self._canceler, self._resetter)
        self._resetter(dc)
        return dc

    def time(self):
        """Return current time."""
        return _time()


class MockClock(object):
    """Provide a deterministic, easily-controlled version of
    L{Clock}.

    This is commonly useful for writing deterministic unit tests for
    code which schedules events using this API.
    """
    right_now = 0.0

    def __init__(self):
        self.calls = []

    def time(self):
        """Pretend to be time.time()."""
        return self.right_now

    def call_later(self, seconds, fn, *a, **kw):
        dc = DelayedCall(self, self.time() + seconds,
                         fn, a, kw, self.calls.remove, lambda c: None)
        self.calls.append(dc)
        self.calls.sort(lambda a, b: cmp(a.time, b.time))
        return dc

    def sleep(self, amount=0):
        """Sleep current greenlet for the specified amount."""
        ev = Event()
        self.call_later(amount, ev.set)
        ev.wait()

    def advance(self, amount=0):
        """Move time on this clock forward by the given amount and run
        whatever pending calls should be run.
        """
        # First we yield the control so that other greenlets have a
        # chance to run.
        gevent_sleep()

        future = self.right_now + amount
        while self.calls and self.calls[0].time <= future:
            dc = self.calls.pop(0)
            self.right_now = dc.time
            dc()
            gevent_sleep()
        self.right_now = max(future, self.right_now)


def patch_gevent(c=None, time=False):
    """Patch gevent itself so that gevent.sleep and gevent.spawn_later
    uses a clock.

    @param time: If true, also patch C{time.time} to use the clock.
    """
    if c is None:
        c = Clock()

    _gevent = __import__('gevent')
    _gevent.sleep = c.sleep
    # FIXME: we need to wrap this in something that looks like a
    # greenlet so that it can be killed with gevent.kill.
    _gevent.spawn_later = c.call_later

    if time:
        _time = __import__('time')
        _time.time = c.time


def restore_gevent():
    time = __import__('time')
    time.time = _time
    _gevent = __import__('gevent')
    _gevent.sleep = gevent_sleep
    _gevent.spawn_later = spawn_later


if __name__ == '__main__':
    def test(c):
        def fn(*args, **kw):
            print c.time(), "fn", args, kw
        c.call_later(2, fn, 1, 2, a="a", b="b")
        print "start to sleep"
        c.sleep(2)
        print "back again"

    def test2():
        import gevent
        import time

        def fn(*args, **kw):
            print time.time(), "fn", args, kw
        print "start to sleep"
        gevent.spawn_later(2, fn, 1, 2, a="a", b="b")
        gevent.sleep(2)
        print "back again"

    c = MockClock()
    gevent.spawn(test, c)
    c.advance(4)
    patch_gevent(c, time=True)
    gevent.spawn(test2)
    c.advance(4)
