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

import persistent
import zope.component.testing
import zope.component.hooks
from zope.site import folder

from p01.oid import oid


class MySite(folder.Folder):
    """Sample site."""

    def __repr__(self):
        return '<%s>' % self.__class__.__name__


class MyObject(persistent.Persistent, oid.OIDAware):
    """Sample object."""

    __name__ = __parent__ = None

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.name)

def setUpOID(test=None):
    zope.component.hooks.setHooks()


def tearDownOID(test=None):
    zope.component.hooks.resetHooks()
    zope.component.testing.tearDown()
