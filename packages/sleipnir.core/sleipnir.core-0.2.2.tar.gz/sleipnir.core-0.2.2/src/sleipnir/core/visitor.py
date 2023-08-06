#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Visitor Pattern

Implementation of the Visitor pattern (GOF94) idiom in Python
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__status__  = "alpha"
__version__ = "0.1"
__date__    = "19 January 2010"
__license__ = "Unknown"
__credits__ = ["Petter Hoffman <ph@petter-hoffmann.com"]

# Import Here any required modules for this module.
import sys

__all__ = ['Visitor']


# pylint: disable-msg=R0921
class Visitor(object):
    """
    A Visitor Patter Idiom for Python

    In order to make use of this pattern, you should derivate from
    this class and implement 'visit_ClassName' methods, where
    ClassName are those class you want visit to

    A 'NotImplementedError' will be raised whenever a valid
    visit_ClassName method couldn't be found
    """

    def __init__(self, stream=sys.stdout):
        super(Visitor, self).__init__()
        self.stream = stream

    def visit(self, node, *args, **kwargs):
        """Invoke to visit 'node' class instance"""

        meth = None
        for cls in node.__class__.__mro__:
            meth_name = 'visit_' + cls.__name__
            meth = getattr(self, meth_name, None)
            if meth:
                break

        if not meth:
            meth = self.generic_visit
        return meth(node, *args, **kwargs)

    def visit_children(self, node, *args, **kwargs):
        """Call this method to visit all 'node' instance children"""

        if '__iter__' in node:
            for child in node:
                self.visit(child, *args, **kwargs)

    def generic_visit(self, node, *args, **kwargs):
        """
        A generic method to be executed when a custom visit_ClassName
        couldn't be found

        By default, Visitor Class raises a
        'NotImplementedMethod'. Override this method to handle in a
        different way
        """

        raise NotImplementedError(
            "Generic visitor for '" + node.__class__.__name__ + "' class")
