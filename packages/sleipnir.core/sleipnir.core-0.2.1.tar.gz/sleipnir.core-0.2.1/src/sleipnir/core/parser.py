#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Regular expresion based Parser for Sleipnir

parser provides with required classes to be able to implement a file
or stream parser based on a set of regular expresions. Just inherit
from Parser Class and define a set of tokens in order of precedence.

See Parser class help for details
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__status__  = "pre-alpha"
__version__ = "0.1"
__date__    = "19 January 2010"
__license__ = "See LICENSE file for details"

# Import Here any required modules for this module.
import os
import io
import odict
from itertools import ifilter
from functools import wraps

__all__ = ['Parser', 'BadTokenError']

from .event import Event
from .log import log


class BadTokenError(Exception):
    """
    A simple exception to be raised when a a problem arises while
    procecessing a token
    """


class StopParser(Exception):
    """Raised to stop parser to examine for more tokens"""


class Parser(object):
    """
    A regex based Parser

    Two are the core components of this kind of parser:
    - A set of tokens. This dictionary based property defines a set of
      well-formed regular expresions
    - A group of events. For each token defined, an event that matches
      token key name will be fired whenever a valid token is found in
      the stream

     On __init__, you should compile a self.regex regular expresion based
     on self.tokens,  previously defined. A method of the form on_<TOKEN>
     will be invoked to precess regular expresion matches. If this method
     exists and returns True, TOKEN_NAME event is fired
    """
    def __init__(self):
        self._buffer = []
        self._events = {}
        self._stream = None
        self._tokens = odict.odict()

    def __getattr__(self, name):
        try:
            return self._events[name]
        except KeyError:
            raise AttributeError(name)

    @property
    def tokens(self):
        """Dict of valid regular expresion patterns"""
        return self._tokens

    @property
    def events(self):
        """Dict of events asocciated with tokens"""
        if not self._events or len(self._events) < len(self._tokens):
            for tok in self._tokens.keys():
                if tok not in self._events:
                    self._events[tok] = Event(tok)
        return self._events

    def stop(self):
        """Stop an active parse operation"""
        raise StopParser

    def parse(self, handler, line_by_line=False):
        """
        Parse handler based on previously defined tokens

        Keyword arguments:
        handler -- A valid file or stream, or a location of a file to
        be parsed
        line_by_line -- Set to True to lookup for tokens line by line

        """

        pthmax = 1024
        if type(handler) in (str, buffer) and os.path.exists(handler[:pthmax]):
            handler = io.open(handler, "r")
        if hasattr(handler, 'read'):
            handler = handler.read()

        self._stream = handler.splitlines(True) if line_by_line else [handler]
        for line in ifilter(lambda x: len(x) > 0, self._stream):
            self._buffer.append(line)
            line = "".join(self._buffer)
            try:
                # For each regular expresion (scanner_Foo)
                for attr in ifilter(lambda x: x.startswith('scanner_'), dir(self)):
                    # Try a match.
                    for mth in getattr(self, attr)().finditer(line):
                        if not mth.lastindex:
                            continue
                        mrange = range(1, mth.lastindex + 1)
                        #pylint: disable-msg=W0108
                        for index in ifilter(lambda x: mth.group(x), mrange):
                            try:
                                token = self._tokens.keys()[index - 1]
                                event = getattr(self, "on_" + token)
                                retvl = event(self, group=mth.group, index=index)
                                self._buffer = []
                            except BadTokenError, ex:
                                log.parser.critical(ex.message)
                                continue
                            except AttributeError, ex:
                                log.parser.debug("Ignored token '%s'" % ex.message)
                                continue
                            if retvl:
                                # Fire an Event if token procesor was a success
                                self.events[token].emit(token, retvl)
                else:
                    if self._buffer:
                        raise NotImplementedError(line[20:] + '...')
            except StopParser:
                break

    @staticmethod
    def group(value):
        """
        Allow to simplify on_TOKEN method declaration by retrieving
        only 'group' with 'index' available as kwargs[value]
        """
        #pylint: disable-msg=C0111
        def wrap(func):
            @wraps(func)
            #pylint: disable-msg=W0613
            def wrapper(self, *args, **kwargs):
                return func(self, kwargs['group'](kwargs[value]))
            return wrapper
        return wrap
