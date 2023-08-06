#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Decorators"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "LGPL"


# Import Here any required modules for this module.
import __builtin__

from sys import argv
from warnings import warn
from subprocess import Popen, PIPE
from functools import wraps, partial

__all__ = ['profile', 'deprecated', ]

# local submodule requirements


#pylint: disable-msg=C0103, R0903
class profile(object):
    """A class decorator which profiles a callable"""

    counter = 0

    def __init__(self, filename=None, standalone=False, dot=True, threshold=1):
        self.standalone = standalone
        self.filename = filename or argv[0]
        self.threshold = threshold
        self.dot = dot
        self.stats = []

    def __call__(self, func):
        @wraps(func)
        def new_func(*args, **kwargs):
            """ A wrapper for func"""
            try:
                from pstats import Stats
                from cProfile import Profile
            except:
                if '__profile__' in __builtin__.__dict__:
                    import sys
                    sys.stderr.write('Disabling profiling: Requirements unmet')
                    del __builtin__.__dict__['__profile__']
                
            if not '__profile__' in __builtin__.__dict__:
                return func(*args, **kwargs)

            filename = "".join(self.filename)
            if self.standalone:
                filename = "".join((func.__name__, str(self.counter),))
                self.counter += 1
            profile_name = "".join((filename, '.profile',))

            # load previous stats
            prof = Profile()
            retv = prof.runcall(func, *args, **kwargs)
            if profile_name in self.stats:
                stats = Stats(profile_name).strip_dirs()
                stats.add(prof)
            else:
                self.stats.append(profile_name)
                stats = Stats(prof).strip_dirs()
            stats.dump_stats(profile_name)

            # create profile diagram
            # pylint: disable-msg=W0612, W0702
            if self.dot:
                threshold = self.threshold
                dot = "dot -Tpng -o %(filename)s.png" % locals()
                gprof = "gprof2dot.py -n %(threshold)s -e "\
                    "%(threshold)s -f pstats %(profile_name)s" % locals()
                try:
                    cmd1 = Popen(gprof.split(), stdout=PIPE)
                    cmd2 = Popen(dot.split(), stdin=cmd1.stdout)
                except:
                    pass
            return retv
        # return decorator
        return new_func


class deprecated(object):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""

    def __init__(self, version="'soon'", ext="."):
        self.version = version
        self.warning = "Called deprecated '%s' method. To be removed %s" + ext

    def __call__(self, func):
        @wraps(func)
        def new_func(*args, **kwargs):
            """A wrapper for func"""
            warn(
                self.warning % (func.__name__, self.version),
                category=DeprecationWarning,
                stacklevel=2)

            return func(*args, **kwargs)
        return new_func


class cached(object):
    """
    Decorator that caches a function's return value each time it is
    called. If called later with the same arguments, the cached value
    is returned, and not re-evaluated.
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        try:
            return self.cache[args]
        except KeyError:
            value = self.func(*args)
            self.cache[args] = value
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return partial(self.__call__, obj)
