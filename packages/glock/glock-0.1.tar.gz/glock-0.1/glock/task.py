# Copyright 2012 Johan Rydberg.
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

import logging
import gevent

log = logging.getLogger(__name__)


class LoopingCall(object):
    """Abstraction for calling a function within intervals."""

    def __init__(self, clock, fn, *args, **kw):
        self.clock = clock
        self.fn = fn
        self.args = args
        self.kw = kw
        self.greenlet = None
        self.interval = 0
        self.running = 0

    def run(self):
        """Loop over the function."""
        try:
            while self.running:
                t0 = self.clock.time()
                self.fn(*self.args, **self.kw)
                t1 = self.clock.time()
                dt = self.interval - (t1 - t0)
                if dt > 0:
                    self.clock.sleep(dt)
        except Exception:
            log.exception('caught exception in looping call')
        finally:
            self.running = 0

    def start(self, interval, now=True):
        """Start calling the function."""
        self.running = 1
        self.interval = interval
        if now:
            gevent.spawn(self.run)
        else:
            self.clock.call_later(self.interval, gevent.spawn,
                    self.run)

    def close(self):
        """Stop calling the function."""
        self.running = 0
