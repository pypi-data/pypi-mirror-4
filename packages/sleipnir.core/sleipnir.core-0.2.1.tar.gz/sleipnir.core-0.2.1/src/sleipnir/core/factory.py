# -*- mode:python; coding: utf-8 -*-

"""
AbstractFactory

Implementation of the AbstractFactory Pattern (GOF94) idiom in Python
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.
from itertools import ifilter

__all__ = ['AbstractFactory']

# local submodule requirements
from .singleton import Singleton


class AbstractFactoryError(Exception):
    """AbstractFactory error"""


class AbstractFactory(Singleton):
    """
    Allows to internally build a valid abstract for args passsed to
    'can_handle' method of declared abstracts

    As a contract, Something smells like a Abstract sii:
      o It's registered into AbstractFactory
      o Implements a class method called 'can_handle'
    """

    ignore_subsequents = True

    def __init__(self, error=AbstractFactoryError):
        super(AbstractFactory, self).__init__()
        self._ex_error = error
        self._backends = {}

    def __contains__(self, key):
        return key in self.backends

    def __iter__(self):
        return self._backends.iteritems()

    @property
    def backends(self):
        """Get registered backends"""
        return self._backends

    def create(self, *args, **kwargs):
        """Build a valid abstract"""
        has_handle = lambda x: hasattr(x, 'can_handle')
        for backend in ifilter(has_handle, self._backends.itervalues()):
            if not backend.can_handle(*args, **kwargs):
                continue
            creator = backend.new  if hasattr(backend, 'new') else backend
            return creator(*args, **kwargs)
        else:
            raise self._ex_error(args)

    def register(self, name, backend):
        """Registry a class implementations as a candidate abstract"""
        if name in self._backends:
            raise TypeError('Already defined %s: %s' % (name, backend))
        self._backends[name] = backend
