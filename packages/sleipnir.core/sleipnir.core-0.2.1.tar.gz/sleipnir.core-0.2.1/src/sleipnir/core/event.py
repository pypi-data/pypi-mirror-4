#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
A non-loop based Event object following Observer pattern (GOF94)

Although most event sistems make use of a event loop to notify about
events into an aplications, (commonly known as Signals), this module
provides an Event class which secuentially notifies listeners about
clients of events occurred.
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import Here any required modules for this module.
from inspect import getargspec
from itertools import chain

__all__ = ['Event', 'EventCallback', 'EventError']


class EventError(Exception):
    """An event esception"""


class EventCallback(object):
    """A Class to wrap """
    def __init__(self, func, detail=None):
        self._wrapps = func
        self._detail = detail

        # verify that callable can process variable keywords.
        # if not, omit event details
        self._args = []
        if hasattr(self._wrapps, 'func'):
            func = self._wrapps.func
        args, _, self._ignvkw, defaults = getargspec(func)
        # compute args
        for pos, arg in enumerate(args):
            if arg in (Event.EV_OWNER, Event.EV_DETAIL,):
                self._args.append((pos, arg,))
        for arg in defaults or []:
            if arg in (Event.EV_OWNER, Event.EV_DETAIL,):
                self._args.append((None, arg,))

    def __call__(self, *args, **kwargs):
        if self._ignvkw is None:
            args = list(args)
            for pos, arg in self._args:
                args.insert(pos, kwargs[arg]) if pos is not None \
                    else args.append(kwargs[arg])
            kwargs.clear()
        return self._wrapps(*args, **kwargs)

    @property
    def detail(self):
        """
        Returns, if present, detailed event to which this
        EventCallback is subscribed
        """
        return self._detail

    @property
    def func(self):
        """
        Returns a weakref to the closure to be called when an event is
        received
        """
        return self._wrapps


class Event(object):
    """
    Implements the observer pattern (GOF94) in a Pythonic way

    User operator overloading '+=' or 'connect' methods to add a
    callable to be executed when a fire event is emmited with 'emit'.

    'Detailed' events are allowed. Construct event instance with a
    tuple which defines event details and connect EventCallbacks as
    described before which a 'detail' value that match any of the
    event details
    """

    EV_OWNER = 'ev_owner'
    EV_DETAIL = 'ev_detail'

    #pylint: disable-msg=W0102
    def __init__(self, name, details=[None, ], owner=None):
        self._name = name
        self._owner = owner
        self._details = details
        self._handlers = {}

    def __iadd__(self, handler):
        assert isinstance(handler, EventCallback)
        self.__event_sanity(handler.detail)
        self._handlers.setdefault(handler.detail, []).append(handler)
        return handler

    def __isub__(self, handler):
        assert isinstance(handler, EventCallback)
        self._handlers[handler.detail].remove(handler)
        return handler

    def __event_sanity(self, detail):
        """
        Check that 'detail' is a valid (previously defined detail
        event for this instance
        """
        if detail not in self._details:
            if detail is None:
                raise EventError(
                    "'%s': Only detailed events are allowed" %
                    self._name)
            else:
                raise EventError(
                    "'%s::%s' detailed event not supported" %
                    (self._name, detail,))

    @property
    def name(self):
        """Event's event name"""
        return self._name

    @property
    def handlers(self):
        """Get registered handlers"""
        return self._handlers

    def connect(self, handler, detail=None):
        """
        Connect handler to this event instance at the end of the queue

        Keyword arguments:
        handler -- a Callable or an instance method.

        """
        event = self.remove(handler, detail)
        if event is None:
            event = EventCallback(handler, detail)
        return self.__iadd__(event)

    def prepend(self, handler, detail=None):
        """
        Connect handler to this event instance at the beginning of the
        queue

        Keyword arguments:
        handler -- a Callable or an instance method.

        """
        event = self.remove(handler, detail)
        if event is None:
            event = EventCallback(handler, detail)
        self._handlers.setdefault(event.detail, []).insert(0, event)
        return event

    def remove(self, handler, detail=None):
        """
        Remove handler from this event instance.

        Keyword arguments:
        handler -- A Callable or an instance method

        """
        assert not isinstance(handler, EventCallback)
        handler = self.find(handler, detail)
        if handler is not None:
            return self.__isub__(handler)

    def find(self, handler, detail=None):
        """
        Finds a callback whose callable is handler and which it's
        connected to detail signal
        """
        if hasattr(handler, 'im_self'):
            fnc = lambda x: getattr(x.func, 'im_self', None) == handler.im_self
        elif isinstance(handler, object):
            fnc = lambda x: x.func == handler
        else:
            return None
        for inst in self._handlers.get(detail, []):
            if fnc(inst):
                return inst
        return None

    def emit_detail(self, detail, *args, **kwargs):
        """
        Fires event

        Keyword arguments:
        detail -- A valid detail to this event. Only connected
        handlers to this 'detail' will respond to the event
        """
        kwargs.setdefault(self.EV_DETAIL, detail)
        self.emit(*args, **kwargs)

    def emit(self, *args, **kwargs):
        """Fires event"""

        kwargs.setdefault(self.EV_OWNER, self._owner)
        for handler in self.get_handlers(**kwargs):
            handler(*args, **kwargs)

    def get_handlers(self, **kwargs):
        """returns an interable of valid handlers for kwargs"""

        detail = kwargs.get(self.EV_DETAIL, None)
        self .__event_sanity(detail)

        # Also fire event for non detailed handlers (lke hook)
        # if None in available handlers
        handlers = self._handlers
        if detail is not None:
            return chain(handlers.get(detail, []), handlers.get(None, []))
        return chain(*handlers.values())
