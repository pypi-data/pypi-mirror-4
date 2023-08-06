#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
A Callback wrapper for python methods that allow to omit optional args
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import Here any required modules for this module.
from inspect import getargspec

__all__ = ['Callback', ]


#pylint:disable-msg=R0903
class Callback(object):
    """A Class to wrap """
    def __init__(self, func):
        self._wrapps = func
        self._length = 0

        # if fun is wrapped by partial, we need to calculate args
        # appropiately
        if hasattr(self._wrapps, 'func'):
            func = self._wrapps.func
            self._length = len(self._wrapps.args)

        # calculate number of fixes args of callback. Remove exceeded
        # args if needed
        args, self._args, self._kwargs, _ = getargspec(func)
        self._length = max(len(args) - self._length, 0)

    def __call__(self, *args, **kwargs):
        if not self._args:
            args = args[:self._length]
        return self._wrapps(*args)

    @property
    def func(self):
        """
        Returns a weakref to the closure to be called when an event is
        received
        """
        return self._wrapps
