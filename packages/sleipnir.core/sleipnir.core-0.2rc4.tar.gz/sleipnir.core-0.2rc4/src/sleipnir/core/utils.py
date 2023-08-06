#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
utils

A set of useful utils
"""

from __future__ import absolute_import

__author__  = "Ask Solem"
__license__ = "BSD, See LICENSE file for details"

# Import here any required modules.
from uuid import UUID, uuid4 as _uuid4, _uuid_generate_random

import sys
import ctypes


def uuid():
    """
    Generate a unique id, having - hopefully - a very small chance of
    collission. For now this is provided by :func:`uuid.uuid4`.
    """
    #pylint: disable-msg=C0111
    def uuid4():
        # Workaround for http://bugs.python.org/issue4607
        if ctypes and _uuid_generate_random:
            uuid_buffer = ctypes.create_string_buffer(16)
            _uuid_generate_random(uuid_buffer)
            return UUID(bytes=uuid_buffer.raw)
        return _uuid4()

    return str(uuid4())


def kwdict(kwargs):
    """
    Make sure keyword arguments are not in unicode.

    This should be fixed in newer Python versions,
    see: http://bugs.python.org/issue4978.
    """
    if sys.version_info >= (3, 0):
        return kwargs
    return dict((key.encode("utf-8"), value)
                for key, value in kwargs.items())


def maybe_list(candidate):
    """
    Wrap candidate into a list. If candidate is None, return an empty
    list. If it's an iterable, return that iterable
    """
    if candidate is None:
        return []
    if hasattr(candidate, "__iter__"):
        return candidate
    return [candidate]
