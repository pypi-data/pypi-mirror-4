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

import BTrees
import persistent
import zope.interface
import zope.location
from zope.container import contained
from zope.security.proxy import removeSecurityProxy

from p01.oid.api import addObject
from p01.oid.api import removeObject

from p01.oid import interfaces
from p01.oid import oid


class OIDContainer(persistent.Persistent, contained.Contained):
    """This class provides a container which stores objects by it's oid as key.
    
    This container does:

    - not notify ObjectAddedEvent and ObjectRemovedEvent
    
    - uses an iteger or long as key given from the ZODB
    
    - locate the items with the given unicode coverted key

    - offer an add method which uses the object oid as key
    
    - offer a remove method which uses the oid argument as key
    """

    zope.interface.implements(interfaces.IOIDContainer)

    family = BTrees.family64 # important since we store oid which are long/int

    def __init__(self):
        super(OIDContainer, self).__init__()
        self.__data = self.family.IO.BTree()

    def keys(self):
        """Returns an object or the given default value.
        
        The method allows to use an integer as sting or unicode.
        """
        return self.__data.keys()

    def __iter__(self):
        return iter(self.__data)

    def __getitem__(self, key):
        if not isinstance(key, int):
            try:
                key = int(key)
            except ValueError:
                raise KeyError("Given oid is not convertable to integer")
        return self.__data[key]

    def get(self, key, default=None):
        """Returns an object or the given default value.
        
        The method allows to use an integer as sting or unicode.
        """
        if not isinstance(key, int):
            try:
                key = int(key)
            except ValueError:
                return default
        return self.__data.get(key, default)

    def values(self):
        return self.__data.values()

    def __len__(self):
        return len(self.__data)

    def items(self):
        return self.__data.items()

    def __contains__(self, key):
        if not isinstance(key, int):
            try:
                key = int(key)
            except ValueError:
                raise KeyError("Given oid is not convertable to integer")
        return self.__data.has_key(key)

    has_key = __contains__

    def __setitem__(self, key, obj):
        """See interface IWriteContainer"""
        # ensure that we use an iteger as key
        if obj.oid != int(key):
            raise KeyError("Key is not equal object oid %s" % obj.oid, key) 
        # now add the object
        self.__data[obj.oid] = obj
        # and locate them
        zope.location.locate(obj, self, unicode(obj.oid))

    def __delitem__(self, key):
        """See interface IWriteContainer"""
        key = int(key)
        obj = self.__data[key]
        del self.__data[key]
        removeObject(obj)
        # unlocate, take care, permission lookup doesn't work after unlocate.
        obj = removeSecurityProxy(obj)
        obj.__name__ = None
        obj.__parent__ = None

    def add(self, obj):
        oid = obj.oid
        if oid is None:
            oid = addObject(obj, self)
        # now add the object
        self.__data[oid] = obj
        # and locate them
        zope.location.locate(obj, self, unicode(oid))
        return oid

    def remove(self, obj):
        removeObject(obj)
        del self.__data[int(obj.__name__)]
        # unlocate, take care, permission lookup doesn't work after unlocate.
        obj = removeSecurityProxy(obj)
        obj.__name__ = None
        obj.__parent__ = None

    def cut(self, key):
        obj = self[key]
        # remove without unlocate and do not remove oid
        del self.__data[key]
        return obj


class OIDItem(persistent.Persistent, contained.Contained, oid.OIDAware):
    """OIDAware item implementation."""

    zope.interface.implements(interfaces.IOIDItem)
