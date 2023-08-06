#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Evaluators. A simple class to check if a set of conditions are
satisfied
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "LGPL"

# Import Here any required modules for this module.
from inspect import isfunction, getmembers
from itertools import compress, imap

__all__ = ['Evaluate', ]

# local submodule requirements


#pylint: disable-msg=R0903
class Evaluate(object):
    """ Abstract class to evaluate iterable params"""

    LAST, CURRENT, STATE = xrange(3)

    def __init__(self, func, iterable):
        self._props = {}
        self._func = func
        self._iterable = iterable

        # find valid values and fill data
        for func in [x for _, x in getmembers(self) if isfunction(x)]:
            try:
                value = compress(iterable, imap(func, iterable)).next()
                fname = func.func_name
                self._props.setdefault(fname, [func(value), None, False])
            except StopIteration:
                pass

    def evaluate(self, **kwargs):
        """
        Evaluate property name against value. Returns true if associated func
        to name is True and object evaluator also returns True, otherwise
        False is returned
        """
        evaluate = False
        for key, value in kwargs.iteritems():
            try:
                func = getattr(self, "".join(('_', key,)))
                prop = self._props[key]
                # update prop value
                prop[self.CURRENT] = value
                prop[self.STATE] = func()
                if prop[self.STATE]:
                    evaluate = True
            except AttributeError:
                pass

        # evaluate
        if evaluate:
            if self._func([x[self.STATE] for x in self._props.itervalues()]):
                for prop in self._props.itervalues():
                    prop[self.STATE] = False
                return True
        return False

    @classmethod
    def can_handle(cls, iterable):
        """
        Class method to check if this vlass can handle 'iterable'
        parameters
        """
        iterable = cls.__dict__.itervalues()
        validate = [x for x in iterable if isfunction(x)]
        for validator in validate:
            if not any(imap(validator, iterable)):
                return False
        return True
