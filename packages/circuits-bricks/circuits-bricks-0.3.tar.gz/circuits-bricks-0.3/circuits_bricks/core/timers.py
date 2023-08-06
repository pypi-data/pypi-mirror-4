"""
..
   This file is part of the circuits bricks component library.
   Copyright (C) 2012 Michael N. Lipp

.. moduleauthor:: mnl

Another implementation of timers. Instead of being event sources themselves,
the timer component register at a TimerSchedule. The schedule keeps the
timers according to their alarm time and generates events for timers
that have expired. This is a more efficient approach if you use a large
number of timers in your application.  
"""

from circuits.core.handlers import handler
from circuits.core.utils import findcmp
from time import time, mktime
from datetime import datetime
from circuits.core.components import BaseComponent
from threading import RLock

class TimerSchedule(BaseComponent):
    
    singleton = True
    _timers = []
    
    def add_timer(self, timer):
        i = 0;
        while i < len(self._timers) and timer.expiry > self._timers[i].expiry:
            i += 1
        self._timers.insert(i, timer)
    
    def remove_timer(self, timer):
        self._timers.remove(timer)

    @handler("generate_events")
    def _on_generate_events(self, event):
        now = time()
        expired = [timer for timer in self._timers if timer.expiry <= now]
        if expired:
            for timer in expired:
                timer.trigger()
            event.reduce_time_left(0)
        next_at = self.next_expiry()
        if next_at is not None:
            event.reduce_time_left(next_at - now)

    def next_expiry(self):
        if len(self._timers) == 0:
            return None
        return self._timers[0].expiry


class Timer(BaseComponent):
    """
    A timer is a component that fires an event once after a certain
    delay or periodically at a regular interval.
    """

    def __init__(self, interval, event, *channels, **kwargs):
        """
        :param interval: the delay or interval to wait for until
            the event is fired. If interval is specified as
            datetime, the interval is recalculated as the time span from
            now to the given datetime.
        :type interval: datetime or float number

        :param event: the event to fire.
        :type event: :class:`~.events.Event`

        If the optional keyword argument *persist* is set to ``True``,
        the event will be fired repeatedly. Else the timer fires the
        event once and then unregisters itself.
        """
        super(Timer, self).__init__()
        self._schedule = None
        self._lock = RLock()

        if isinstance(interval, datetime):
            self.interval = mktime(interval.timetuple()) - time()
        else:
            self.interval = interval

        self.event = event
        self.channels = channels

        self.persist = kwargs.get("persist", False)

        self._eTime = time() + self.interval

    @handler("registered", channel="*")
    def _on_registered(self, component, manager):
        if self._schedule is None:
            if isinstance(component, TimerSchedule):
                self._schedule = component
            elif component == self:
                component = findcmp(self.root, TimerSchedule)
                if component is not None:
                    self._schedule = component
                else:
                    self._schedule = TimerSchedule().register(manager.root)
            if self._schedule is not None:
                self._schedule.add_timer(self)

    def unregister(self):
        with self._lock: # Concurrent reset may interfere
            if self._schedule is not None:
                self._schedule.remove_timer(self)
                self._schedule = None
        super(Timer, self).unregister()

    def trigger(self):
        self.fire(self.event, *self.channels)

        if self.persist:
            self.reset()
        else:
            self.unregister()

    def reset(self):
        """
        Reset the timer, i.e. clear the amount of time already waited
        for.
        """
        with self._lock: # Concurrent unregister may interfere
            if self._schedule is not None:
                self._schedule.remove_timer(self)
            self._eTime = time() + self.interval
            if self._schedule is not None:
                self._schedule.add_timer(self)

    @property
    def expiry(self):
        return getattr(self, "_eTime", None)
    