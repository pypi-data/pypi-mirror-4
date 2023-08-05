##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
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

from ZODB.utils import p64
from ZODB.utils import u64
from ZODB.POSException import ConnectionStateError
from ZODB.POSException import POSKeyError

from zope.security.proxy import removeSecurityProxy
from zope.component import hooks


def _queryCon(cur):
    if getattr(cur, '_p_jar', None):
        return cur._p_jar
    while not getattr(cur, '_p_jar', None):
        cur = getattr(cur, '__parent__', None)
        if cur is None:
            return None
    return cur._p_jar


def queryConnection(obj, context=None):
    """Returns a connection based on obj, context or site."""
    conn = _queryCon(obj)
    if conn is None and context is not None:
        conn = _queryCon(context)
    if conn is None:
        site = hooks.getSite()
        conn = _queryCon(site)
    return conn


def addObject(obj, context=None):
    obj = removeSecurityProxy(obj)
    if obj.oid is None:
        if obj._p_oid is None:
            # if _p_oid is None, try to add the obj to the connection
            conn = queryConnection(obj, context)
            conn.add(obj)
        obj._oid = u64(obj._p_oid)
    return obj.oid


def removeObject(obj):
    removeSecurityProxy(obj)._oid = None


def getObject(oid, context=None):
    if context is None:
        context = hooks.getSite()
    conn = queryConnection(context)
    try:
        obj = conn.get(p64(int(oid)))
        if getattr(obj, 'oid', None) is not None:
            return obj
    except (ConnectionStateError, POSKeyError), e:
        pass
    raise KeyError(oid)


def queryObject(oid, context=None, default=None):
    if oid is None:
        return None
    try:
        return getObject(oid, context)
    except (AttributeError, KeyError, ValueError), e:
        # AttributeError happens if _p_jar is not defined (testing)
        # KeyError happens if getObject doesn't find an object
        # ValueError happens if oid is not convertable to int
        pass
    return default


def yieldObjects(oids, context=None):
    """Optimized yield object method.
    
    Only pass a context as argument if the context is available in the 
    connection otherwise an ISite is used as context.
    """ 
    if context is None:
        context = hooks.getSite()
    conn = context._p_jar
    for oid in oids:
        try:
            obj = conn.get(p64(oid))
            if getattr(obj, 'oid', None) is not None:
                yield obj
        except (ConnectionStateError, POSKeyError), e:
            pass
