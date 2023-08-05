##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
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
$Id:$
"""
__docformat__ = "reStructuredText"

import logging
import memcache
import cPickle
import threading
import types
try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5

import zope.interface
from zope.schema.fieldproperty import FieldProperty
from p01.memcache import interfaces

TLOCAL = threading.local()

log = logging.getLogger('p01.memcache')


class MemcacheClient(object):
    """Non persistent memcached client uasable as global utility."""

    zope.interface.implements(interfaces.IMemcacheClient)

    _memcacheClientFactory = memcache.Client

    servers = FieldProperty(interfaces.IMemcacheClient['servers'])
    debug = FieldProperty(interfaces.IMemcacheClient['debug'])
    namespace = FieldProperty(interfaces.IMemcacheClient['namespace'])
    lifetime = FieldProperty(interfaces.IMemcacheClient['lifetime'])
    pickleProtocol = FieldProperty(interfaces.IMemcacheClient['pickleProtocol'])

    def __init__(self, servers=['127.0.0.1:11211'], debug=0, pickleProtocol=-1,
        lifetime=None, namespace=None):
        self.servers = servers
        self.debug = debug
        self.pickleProtocol = pickleProtocol
        if lifetime is not None:
            self.lifetime = lifetime
        if namespace is not None:
            self.namespace = namespace

    def buildKey(self, key):
        """Builds a (md5) memcache key based on the given key

        - if the key is a string, the plain key get used as base

        - if the key is unicode, the key get converted to UTF-8 as base

        - if the key is an int, the key get converted to string as base

        - if key is a persistent object its _p_oid is used as base

        - anything else will get pickled (including unicode)
        
        Such a base key get converted to an md5 hexdigest if a namespace is
        used, the namespace is used as key prefix.

        """
        if isinstance(key, (types.IntType, types.StringType)):
            bKey = str(key)
        elif isinstance(key, types.UnicodeType):
            bKey = key.encode('UTF-8')
        elif getattr(key, '_p_oid', None):
            bKey = getattr(key, '_p_oid')
        else:
            bKey = cPickle.dumps(key, protocol=self.pickleProtocol)

        if self.namespace is not None:
            bKey = '%s%s' % (self.namespace, bKey)
        mKey = md5(bKey)
        return mKey.hexdigest()

    def set(self, key, data, lifetime=None, raw=False):
        bKey = self.buildKey(key)
        if lifetime is None:
            lifetime = self.lifetime
        if raw:
            if not isinstance(data, types.StringType):
                raise ValueError(
                    "Data must be a string %s given" % type(data), data)
        else:
            data = cPickle.dumps(data, protocol=self.pickleProtocol)
        if self.debug:
            log.debug('set: %r -> %s, %r, %r, %r' % (key, bKey, len(data),
                self.namespace, lifetime))

        if self.client.set(bKey, data, lifetime):
            return bKey
        return None

    def query(self, key, raw=False, default=None):
        res = self.client.get(self.buildKey(key))
        if res is not None and self.debug:
            log.debug('query: %r, %r, %r, %r' % (key, len(res), self.namespace,
                raw))
        if res is None:
            return default
        if raw:
            return res
        return cPickle.loads(res)

    def invalidate(self, key):
        log.debug('invalidate: %r, %r '% (key, self.namespace))
        self.client.delete(self.buildKey(key))

    def invalidateAll(self):
        self.client.flush_all()

    def getStatistics(self):
        return self.client.get_stats()

    @property
    def client(self):
        sKey = tuple(self.servers)
        mc = TLOCAL.__dict__.get(sKey, None)
        if mc is None:
            mc = self._memcacheClientFactory(self.servers, debug=self.debug,
                pickleProtocol=self.pickleProtocol)
            TLOCAL.__dict__[sKey] = mc
            log.info('Creating new local memcache client for %r' % \
                ', '.join(self.servers))
        return mc
