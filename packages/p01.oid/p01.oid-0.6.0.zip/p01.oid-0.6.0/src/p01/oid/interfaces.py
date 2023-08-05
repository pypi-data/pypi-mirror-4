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

import zope.interface
import zope.schema
import zope.container.interfaces


class IOIDAware(zope.interface.Interface):
    """OID aware object."""

    oid = zope.schema.Int(
        title=u"OID",
        description=u"The object id",
        default=None,
        readonly=False,
        required=False)


class IOIDManager(zope.interface.Interface):
    """Object id management adapter.
    
    This adapter can adapt any persistent object and offers access to the 
    objects located in the same database where the adapted object is stored.
    """

    def add(obj):
        """Add an object will activate the access to the object by apply an oid
        """

    def remove(obj):
        """Remove an object will deactivate the access to the object by remove
        an oid.
        """

    def validate(oid):
        """Returns True if an object is valid if not return False."""

    def getObject(oid):
        """Returns an object by the given object id.
        
        Raises a KeyError if no object can be found e.g. removed objects.
        """

    def queryObject(oid, default=None):
        """Return an object if availble if not return default."""

    def getOID(obj):
        """Returns an object id for the given object.
        
        Raises a KeyError if no object can be found e.g. non persistent objects.
        """

    def queryOID(obj, default=None):
        """Returns an oid if available or default if not."""


class IOIDSearchQuery(zope.interface.Interface):
    """Chainable search query using oids.
    
    This interface is compatible with z3c.indexer IQuery objects except that
    we skip the sort, limit and reverse arguments in searchResults.
    """

    results = zope.interface.Attribute("""List of oids.""")

    def apply():
        """Return iterable search result wrapper."""

    def searchResults(searchResultFactory=None):
        """Returns an searchResultFactory with search result object oids."""

    def Or(query):
        """Enhance search results. (union)

        The result will contain intids which exist in the existing result 
        and/or in the result from te given query.
        """

    def And(query):
        """Restrict search results. (intersection)

        The result will only contain intids which exist in the existing
        result and in the result from te given query. (union)
        """

    def Not(query):
        """Exclude search results. (difference)

        The result will only contain intids which exist in the existing
        result but do not exist in the result from te given query.
        
        This is faster if the existing result is small. But note, it get 
        processed in a chain, results added after this query get added again. 
        So probably you need to call this at the end of the chain.
        """


class IOIDContainer(zope.container.interfaces.IContainer):
    """This class provides a container which stores objects by it's oid as key.
    
    This container does:

    - not notify ObjectAddedEvent and ObjectRemovedEvent
    
    - use an iteger as key
    
    - locate the items with the given unicode coverted key

    - offer an add method which uses the object oid as key
    
    - offer a remove method which uses the oid argument as key
    """

    def add(obj):
        """Add an object to the container using the objects oid as key."""

    def remove(key):
        """Remove an object from the container.
        
        Also unlocate them and remove the oid.
        
        Note: you have to unindex the object in every index before you remove
        an object from the container otherwise you will not have the permission
        to access the object because of a missing location during permission
        lookup.
        """

    def cut(obj):
        """Remove an object from the container without to unlocate them."""


class IOIDItem(IOIDAware):
    """Persistent oid aware item."""


# events
class IOIDEvent(zope.interface.Interface):
    """Generic base interface for events"""

    object = zope.interface.Attribute("The object related to this event")


class IOIDRemovedEvent(IOIDEvent):
    """Before a oid will be removed from the object

    The event get notified BEFORE the oid is removed from the object.
    """


class IOIDAddedEvent(IOIDEvent):
    """After a unique oid get added to the object

    The event get notified AFTER an oid get added to the object.
    """
