#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Singleton Pattern

Implementation of the Singleton Pattern (GOF94) idiom in Python

Just inherit from it and you have a singleton. No code is required in
subclasses to create singleton behavior -- inheritance from Singleton
is all that is needed.

USAGE:

Just inherit from Singleton. If you need a constructor, include an
__init__() method in your class as you usually would. However, if your
class is S, you instantiate the singleton using S.get_instance()
instead of S(). Repeated calls to S.get_instance() return the
originally-created instance.

For example:

class S(Singleton):
    def __init__(self, a, b=1):
        pass

S1 = S.get_instance(1, b=3)

"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__status__  = "alpha"
__version__ = "0.1"
__date__    = "19 January 2010"
__license__ = "Public Domain"
__credits__ = ["Gary Robinson <garyrob@me.com>"]

# Import Here any required modules for this module.

__all__ = ['Singleton']


class SingletonException(Exception):
    """A custom exception for Singleton derived Classes"""


class SingletonMeta(type):
    """Metaclass for Singleton Classes"""

    def __new__(mcs, name, bases, dct):
        if '__new__' in dct:
            raise SingletonException("Can't override '__new__'")
        return type.__new__(mcs, name, bases, dct)

    def __call__(mcs, *args, **kwargs):
        raise SingletonException("Instantiated through get_instance()")


# pylint: disable-msg=R0903
class Singleton(object):
    """
    Singleton Class

    Derive from it in order to create a custom singleton class
    """

    __metaclass__ = SingletonMeta

    @classmethod
    def get_instance(cls, *args, **kwargs):
        """
        Call this to instantiate an instance or retrieve the existing
        instance.

        If the singleton requires args to be instantiated, include
        them the first time you call get_instance.
        """

        if  '_instance' in cls.__dict__:
            if (args or kwargs) and not hasattr(cls, 'ignore_subsequent'):
                raise SingletonException("Already instantiated")
        else:
            instance = cls.__new__(cls)
            try:
                instance.__init__(*args, **kwargs)
            except TypeError, ex:
                if str(ex.message).find('__init__() takes') != -1:
                    raise SingletonException(ex.message)
                else:
                    raise
            cls._instance = instance
        return cls._instance
