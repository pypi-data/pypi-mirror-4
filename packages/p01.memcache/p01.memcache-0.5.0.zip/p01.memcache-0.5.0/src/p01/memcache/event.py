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
__docformat__ = 'restructuredtext'

import zope.interface
import zope.component

from p01.memcache import interfaces


class InvalidateCacheEvent(object):
    zope.interface.implements(interfaces.IInvalidateCacheEvent)

    def __init__(self, key, cacheName=None):
        """Key argument could be an object if the object is used as key."""
        self.key = key
        self.cacheName = cacheName


@zope.component.adapter(interfaces.IInvalidateCacheEvent)
def invalidateCache(event):
    if event.cacheName is not None:
        cache = zope.component.queryUtility(interfaces.IMemcacheClient,
            event.cacheName)
        caches = []
        if cache is not None:
            caches.append(cache)
    else:
        caches = zope.component.getAllUtilitiesRegisteredFor(
            interfaces.IMemcacheClient)

    for cache in caches:
        cache.invalidate(event.key)
