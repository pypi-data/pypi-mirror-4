#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Decorators"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "LGPL"

# Import Here any required modules for this module.
from array import array
from copy import deepcopy

__all__ = ['Cast', ]

# local submodule requirements
from .factory import AbstractFactory


#pylint: disable-msg=R0903,W0232,E1101
class Cast(AbstractFactory):
    """ Allow cast between objects, collections and primary types """
    def __getattr__(self, name):
        if name == 'get':
            return self.create


class MetaCast(type):
    """Section Metaclass"""
    def __init__(mcs, name, bases, dct):
        type.__init__(mcs, name, bases, dct)
        if not name.endswith("Cast"):
            Cast.get_instance().registry((name, mcs))


class BaseCast(object):
    """Base class for Matrix to Matrix castings"""

    __metaclass__ = MetaCast

    def __init__(self, instance):
        self._value = instance

    def _create_tuple(self, size, value, mtype=None):
        """Create a basic tuple"""
        raise NotImplementedError

    def _create_matrix(self, size, value, mtype=None):
        """Create a basic Matrix"""
        #pylint: disable-msg=W0612
        mtx = [self._create_tuple(size, value, mtype) for row in xrange(size)]
        return mtx

    def _copy_matrix(self, mtx, size, mtype=None):
        """Copy a matrix"""
        raise NotImplementedError


class MatrixCast(BaseCast):
    """Base class for List based Matrix"""
    def _create_tuple(self, size, value, mtype=None):
        return [value] * size

    def _copy_matrix(self, mtx, size, mtype=None):
        if type(mtx) == list and type(mtx[0]) == list:
            return deepcopy(mtx)
        return [[mtx[row][col] for col in xrange(size)] \
                    for row in xrange(size)]


class ArrayCast(BaseCast):
    """Base class for Matrix to Array castings"""
    def __init__(self, instance):
        self._typec = {
            float:   'f',
            int:     'l',
            long:    'L',
            str:     'c',
            unicode: 'u',
            }
        super(ArrayCast, self).__init__(instance)

    def _create_tuple(self, size, value, mtype=None):
        return array(self._typec[mtype], [value] * size)

    def _copy_matrix(self, mtx, size, mtype=None):
        if type(mtx) == list and type(mtx[0]) == array:
            return deepcopy(mtx)
        mtype = mtype or type(mtx[0][0])
        return [array(self._typec[mtype],                          \
                          [mtx[row][col] for col in xrange(size)]) \
                    for row in xrange(size)]


class MatrixRoute(object):
    """
    Cast an object accessible as a matrix [][] to an true array
    """
    def __getattr__(self, name):
        for name in (name, name + 's',):
            #pylint: disable-msg=W0703
            try:
                mtrxsize, mtrx = len(self._value(name)), self._value(name)
                if self._value.directed:
                    return self._copy_matrix(mtrx, mtrxsize)
                # create a SxS matrix with default values
                val_type = type(mtrx[0][0])
                nwmtrx = self._create_matrix(mtrxsize, val_type(), val_type)
                # copy contents
                for org in xrange(mtrxsize):
                    for des in xrange(len(mtrx[org]) - 1):
                        col = org + des + 1
                        nwmtrx[org][col] = nwmtrx[col][org] = mtrx[org][des]
                return nwmtrx

            except Exception:
                pass
        raise AttributeError("Unknown '%s' named array", name)

    @classmethod
    def can_handle(cls, instance):
        """Check if cand handle instance"""
        iterable = instance.__class__.__mro__
        return any((cls for cls in iterable if cls.__name__ == 'MatrixRoutes'))

    @classmethod
    # pylint: disable-msg=W0613
    def new(cls, instance, *args):
        """Create an instance"""
        return cls(instance)


class MatrixRouteToArray(MatrixRoute, ArrayCast):
    """
    Cast an Array from a route variable to a normaliced Matrix Array
    """
    @classmethod
    def can_handle(cls, instance, tuple_type):
        """Check if cand handle instance"""
        if tuple_type != type(array):
            return False
        return super(MatrixRouteToArray, cls).can_handle(instance)


class MatrixRouteToMatrix(MatrixRoute, MatrixCast):
    """
    Cast an Array from a route variable to a normaliced List based
    Array
    """
    @classmethod
    def can_handle(cls, instance, tuple_type):
        """Check if cand handle instance"""
        if tuple_type != list:
            return False
        return super(MatrixRouteToMatrix, cls).can_handle(instance)


class MatrixObjectToArray(ArrayCast):
    """
    Cast an object accessible as a matrix [][] to an true array
    """
    def __getattr__(self, name):
        value = getattr(self._value[0][0], name)
        return [array(self._typec[type(value)], [                  \
                    getattr(self._value[row][col], name)           \
                        for col in xrange(len(self._value[row]))]) \
                    for row in xrange(len(self._value))]

    @classmethod
    def can_handle(cls, instance):
        """Check if cand handle instance"""
        try:
            return all([type(child[-1]) == object for child in instance])
        # pylint: disable-msg=W0703
        except Exception:
            return False


class Resize(object):
    """Resize Matrix to a multiple of a 'multiple' array"""

    # pylint: disable-msg=W0102
    def __call__(self, multiple=4, value=[None]):
        mtx_size, mtx = len(self._value), self._value

        # calculate candidate increment
        incr = mtx_size % multiple % multiple
        if incr > 0:
            # calculate default value
            mtx_type = type(mtx[0][0])
            if type(value) != list and value[0] != None:
                value = mtx_type()
            # transform on a full matrix
            for row in xrange(mtx_size):
                mtx[row].extend([value] * incr)
            mtx.extend(                                               \
                [self._create_tuple(mtx_size + incr, mtx_type, value) \
                     for row in xrange(incr)])
        return mtx


class MatrixResize(Resize, MatrixCast):
    """A Cast to resize a Matrix based Matrix"""
    @classmethod
    def can_handle(cls, instance):
        """Check if cand handle instance"""
        if type(instance) != list or len(instance) == 0:
            return False
        if type(instance[0]) != list:
            return False
        return True


class ArrayResize(Resize, ArrayCast):
    """A Cast to resize an Array based Matrix"""

    @classmethod
    def can_handle(cls, instance):
        """Check if cand handle instance"""
        if type(instance) != list or len(instance) == 0:
            return False
        if type(instance[0]) != type(array):
            return False
        return True
