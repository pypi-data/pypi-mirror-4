##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: memcache.py 77359 2007-07-03 15:54:09Z dobe $
"""
__docformat__ = "reStructuredText"

from datetime import datetime
from datetime import timedelta

import zope.component

from p01.memcache import interfaces
from p01.memcache import client

# shared fake memcache data storage, one per memcache client with different
# servers
storage = {}

def getData(servers):
    return storage.setdefault(''.join(servers), {})

_marker = object()


class FakeMemcached(object):
    """Fake memcached server which makes sure to separate data."""

    def __init__(self, servers=['127.0.0.1:11211'], debug=0, pickleProtocol=0):
        self.servers = servers
        self.debug = debug
        self.pickleProtocol = pickleProtocol
        self.cache = getData(servers)
        self.resetCounts()

    def getStats(self):
        return []

    def set(self, key, data, lifetime=0):
        # raise an error if not a string
        str(key)
        str(data)
        if lifetime:
            lifetime = datetime.now()+timedelta(seconds=lifetime)
        else:
            lifetime = None
        self.cache[key] = (data, lifetime)
        self._sets += 1
        return True

    def get(self, key):
        str(key)
        data = self.cache.get(key, _marker)
        self._gets += 1
        if data is _marker:
            self._misses += 1
            return None
        if data[1] is None or datetime.now() < data[1]:
            self._hits += 1
            return data[0]
        del self.cache[key]
        self._misses += 1
        return None

    def delete(self, key):
        if key in self.cache:
            del self.cache[key]

    def flush_all(self):
        storage[''.join(self.servers)] = {}
        self.cache = getData(self.servers)

    @property
    def gets(self):
        return self._gets

    @property
    def hits(self):
        return self._hits

    @property
    def misses(self):
        return self._misses

    @property
    def sets(self):
        return self._sets

    def resetCounts(self):
        self._hits = 0
        self._misses = 0
        self._gets = 0
        self._sets = 0


class FakeMemcacheClient(client.MemcacheClient):
    """A memcache client which doesn't need a running memcache daemon.
    
    This fake client also shares the data accross threads.
    
    This fake MemcacheClient can be used if you need to setup an utility in 
    a test.
    """

    _memcacheClientFactory = FakeMemcached
    _client = None

    def __init__(self, servers=['127.0.0.1:11211'], debug=0, pickleProtocol=-1,
        lifetime=None, namespace=None):
        super(FakeMemcacheClient, self).__init__(servers, debug,
            pickleProtocol, lifetime, namespace)
        # setup fake memcached server
        self._client = self._memcacheClientFactory(self.servers, self.debug,
            self.pickleProtocol)

    @property
    def client(self):
        return self._client

    @property
    def gets(self):
        return self.client.gets

    @property
    def hits(self):
        return self.client.hits

    @property
    def misses(self):
        return self.client.misses

    @property
    def sets(self):
        return self.client.sets

    def resetCounts(self):
        self.client.resetCounts()


_orgMemcacheClientFactory = None

def setUpFakeMemcached(test=None):
    """Patch all existing IMemcachClient utilities.
    
    This method can be used for patch all existing memcache clients at class
    level.
    """
    global _orgMemcacheClientFactory
    storage = {}
    _orgMemcacheClientFactory = client.MemcacheClient._memcacheClientFactory
    client.MemcacheClient._memcacheClientFactory = FakeMemcached
    # setup fake client
    fClient = FakeMemcacheClient()
    zope.component.provideUtility(fClient, interfaces.IMemcacheClient, name='')
    fClient.invalidateAll()


def tearDownFakeMemcached(test=None):
    if _orgMemcacheClientFactory is not None:
        client.MemcacheClient._memcacheClientFactory = _orgMemcacheClientFactory
    storage = {}
