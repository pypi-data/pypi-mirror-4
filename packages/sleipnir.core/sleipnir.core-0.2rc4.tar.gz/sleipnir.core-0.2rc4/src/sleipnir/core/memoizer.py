# -*- mode: python; coding: utf-8 -*-

"""
Memoizer

A Memcached like persistent implementation of a wrapper around dict
like objects that provide serialization and caching
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# import here required values
import datetime

try:
    import cPickle as pickle
except ImportError:
    import pickle


class Memoizer(object):
    """Cache and memoizer."""

    LIFETIME = -1

    def __init__(self, store=dict(), expires=dict(), **kwargs):
        """
        Check store. If it's a file, try to read from int as a
        cPickle and get dictionary readed an use it as store
        """
        # set valid default values
        self._data     = store
        self._expires  = expires
        self._storage  = None
        self._default  = kwargs.get('failover')
        self._failover = 'failover' in kwargs

        # if store is a string, assume it's a pickle location
        if isinstance(store, basestring):
            with open(store, "rb") as source:
                self._data, self._expires = pickle.load(source)
            self._storage = store

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, key):
        self.delete(key)

    def __len__(self):
        len(iter(self))

    def __contains__(self, key):
        """Return if a key exists in the cache."""
        ttl = self.ttl(key)
        return key in self._data if ttl is None or ttl > 0 else False

    def __iter__(self):
        for key, _ in self.iteritems():
            yield key

    def sync(self, where=None):
        """Store current data into cached pointed by where. If no
        value is present, it will try to discover from initial
        values"""
        store = where or self._storage
        with open(store, "eb") as dest:
            pickle.dump((self._data, self._expires), dest, -1)

    def purge(self, timeout=None):
        """Try to remove expires keys from current data"""
        timeout = timeout or datetime.datetime.now()
        # Compute obsolete keys
        expires = self._expires.iteritems()
        expires = [key for key, val in expires if val < timeout]
        # Purge dicts; pylint: disable-msg=W0106
        [self._expires.pop(key) for key in expires]
        [self._data.pop(key)    for key in expires]

    def ttl(self, key):
        """Get time to live for a key. If expired, purge it from system"""
        # compute expiration time
        time = datetime.datetime.now()
        # Try to fetch key. if it's inmutable, return time to compare
        # so condition is applicable
        expires_in = self._expires.get(key)
        # Satisfied when key has expired
        if expires_in is not None:
            delta = expires_in - time
            if delta <= 0:
                self._expires.pop(key)
                self._data.pop(key)
            return delta
        # inmortal key. return None
        return None

    def get(self, key):
        """Manually retrieve a value from the cache, calculating as needed"""
        # this  call will purge obsole key
        self.ttl(key)
        # raise Error if no failover has been defined
        if not self._failover and key not in self._data:
            raise KeyError(key)
        # return data or default value. Failover is accepted
        return self._data.get(key, self._default)

    def set(self, key, value, expires=LIFETIME):
        """
        Set key with value for expires seconds. If not present or
        set to -1, a persistent key will be assumed
        """
        assert isinstance(key, basestring)
        # store expiration, if required
        if expires != self.LIFETIME:
            delta = datetime.timedelta(seconds=int(expires))
            self._expires[key] = datetime.datetime.now() + delta
        # store value
        self._data[key] = value

    def delete(self, key):
        """Remove a key from the cache"""
        self._data.pop(key, None)
        self._expires.pop(key, None)

    def expire_at(self, key, time):
        """Set the explicit expiry time of a key"""
        assert datetime.datetime.now() - time > 0
        assert key in self._data
        self._expires[key] = time

    def expire(self, key, expires):
        """Set the maximum age of a given key, in seconds."""
        delta = datetime.timedelta(seconds=int(expires))
        self.expire_at(key, datetime.datetime.now() + delta)

    def iteritems(self):
        """Iterator over all valid key, value pairs"""
        for key, value in self._data.iteritems():
            time = datetime.datetime.now()
            ttl  = self._expires.get(key, None)
            if ttl is None or ttl - time > 0:
                yield (key, value)
