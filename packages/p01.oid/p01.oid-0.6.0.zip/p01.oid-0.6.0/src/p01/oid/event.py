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

from ZODB.utils import u64

import zope.interface
import zope.component
import zope.component.hooks
import zope.lifecycleevent.interfaces

import p01.oid.api
from p01.oid import interfaces


# events
class OIDRemovedEvent(object):
    """Before a unique oid will be removed from the object

    The event get notified BEFORE the oid get set to NONE. This will allow to
    unindex objects be their oid in catalog indexes beforethe object get
    unaccessible by it's oid.
    """

    zope.interface.implements(interfaces.IOIDRemovedEvent)

    def __init__(self, object):
        self.object = object


class OIDAddedEvent(object):
    """After a unique oid get added to the object

    The event get notified AFTER an oid get applied.
    """

    zope.interface.implements(interfaces.IOIDAddedEvent)

    def __init__(self, object):
        self.object = object


# subscriber
@zope.component.adapter(interfaces.IOIDAware,
                        zope.lifecycleevent.interfaces.IObjectCreatedEvent)
def addOIDSubscriber(obj, event):
    """A subscriber to IObjectCreatedEvent

    Add an _oid based on the _p_oid which will enable access to the object in
    the database
    """
    if obj.oid is None:
        if obj._p_oid is None:
            # add the object to the connection
            conn = p01.oid.api.queryConnection(obj)
            conn.add(obj)
        obj._oid = u64(obj._p_oid)


@zope.component.adapter(interfaces.IOIDAware,
                        zope.lifecycleevent.interfaces.IObjectRemovedEvent)
def removeOIDSubscriber(obj, event):
    """A subscriber to IObjectRemovedEvent

    Removes the _oid which will disable access to the object in the database
    """
    obj._oid = None


@zope.component.adapter(interfaces.IOIDEvent)
def dispatchIOIDEvents(event):
    """Event subscriber to dispatch IOIDEvent to interested adapters."""
    for adapted in zope.component.subscribers((event.object, event), None):
        pass # adapting them does the work
