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

import persistent.interfaces
from ZODB.utils import p64
from ZODB.utils import u64
from ZODB.POSException import ConnectionStateError
from ZODB.POSException import POSKeyError

import zope.interface
import zope.component
from zope.schema.fieldproperty import FieldProperty

import p01.oid.api
from p01.oid import interfaces


class OIDAware(object):
    """OID aware mixin class."""

    zope.interface.implements(interfaces.IOIDAware)
    
    _oid = FieldProperty(interfaces.IOIDAware['oid'])

    @property
    def oid(self):
        return self._oid


class OIDManager(object):
    """Object id management adapter.
    
    This adapter can adapt any persistent object and offers access to the 
    objects located in the same database where the adapted object is stored.
    """

    zope.interface.implements(interfaces.IOIDManager)
    zope.component.adapts(persistent.interfaces.IPersistent)

    def __init__(self, context):
        self.context = context
        self.conn = context._p_jar or p01.oid.api.queryConnection(context)

    def add(self, obj):
        """Add an object will activate the access to the object by apply an oid
        """
        if obj.oid is None:
            if obj._p_oid is None:
                # if _p_oid is None, add the obj to the connection
                self.conn.add(obj)
            obj._oid = u64(obj._p_oid)
        return obj.oid

    def remove(self, obj):
        """Remove an object will deactivate the access to the object by remove
        an oid.
        """
        # just marks an object as removed from the OIDManager, not from the
        # ZODB, you can simply add them back to the OIDManager by set the oid
        # reference e.g. self._oid = self._p_oid
        obj._oid = None

    def validate(self, oid):
        """Returns True if an object is valid if not return False."""
        obj = self.conn.get(p64(oid))
        if obj.oid == oid:
            return True
        return False

    def getObject(self, oid):
        """Returns an object by the given object id."""
        try:
            # yes, we always get the object from the ZODB
            obj = self.conn.get(p64(oid))
            if obj.oid is not None:
                # but we only return them if our oid reference is alive
                # e.g. _oid is not set to None. See remove method above
                return obj
        except (ConnectionStateError, POSKeyError, AttributeError), e:
            pass
        raise KeyError(oid)

    def queryObject(self, oid, default=None):
        """Return an object if availble if not return default."""
        try:
            return self.getObject(oid)
        except KeyError, e:
            pass
        return default

    def getOID(self, obj):
        """Returns an object id for the given object."""
        return obj.oid

    def queryOID(self, obj, default=None):
        """Returns an oid if available or default if not."""
        if obj.oid is not None:
            return obj.oid
        return default

    def __repr__(self):
        return '<%s for %s>' %(self.__class__.__name__, self.context)
