# Glock - a Clock abstraction for gevent #

Most likely your application is in some way working with the concept
of time. It can be timeouts, it can be tasks that should be executed
within regular intervals.

Glock (Gevent cLOCK) tries to encapsulate time-related functionality
into a simple *Clock* class.  Also provided is a mock Clock class
allowing deterministic testing.

Usage:

    from glock.clock import Clock

    c = Clock()
    c.call_later(1, fn)


API:

The `call_later(seconds, fn, *args, **kw)` method calls `fn` *seconds*
from now.  A `DelayedCall` instance is returned that can be used to 
reschedule the call (using `reset`) or cancel it (using `cancel`).

The clock also have a `sleep` method that acts just like
`gevent.sleep`.  To read out the current time, use the `time` method.

The `MockClock` method also has an `advance` method that is used to
advance time in a controlled manner.
