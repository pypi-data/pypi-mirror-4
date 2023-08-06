# -*- mode:python; coding: utf-8 -*-

"""
Imports
"""

from __future__ import absolute_import

__author__ = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.


class Lazy(object):
    """Resolve a class only when it's going to be used"""

    def __init__(self, path, lazy=None):
        self.__path = path
        self.__lazy = lazy

    def __lazy__(self):
        if not self.__lazy:
            module, _, klass = self.__path.partition(":")
            mod = __import__(module, globals(), locals(), [klass])
            self.__lazy = getattr(mod, klass)
        return self.__lazy

    def __call__(self, *args, **kwargs):
        return self.__lazy__()(*args, **kwargs)

    def __getattr__(self, value):
        return getattr(self.__lazy__(), value)

    @property
    def cls(self):
        """Fetch class definition"""
        return self.__lazy__()
