##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
import zope.interface
import zope.component

import p01.oid.api
from p01.oid import interfaces


class OIDResultSet:
    """Lazily accessed set of objects."""

    def __init__(self, oids, context=None):
        self.oids = oids
        self.context = context

    def __len__(self):
        return len(self.oids)

    def __contains__(self, item):
        if item.oid in self.oids:
            return True
        else:
            return False

    def __getitem__(self, slice):
        start = slice.start
        stop = slice.stop
        if stop > len(self):
            stop = len(self)
        return [p01.oid.api.getObject(self.oids[idx], self.context)
                for idx in xrange(start, stop)]

    def __iter__(self):
        for oid in self.oids:
            obj = p01.oid.api.getObject(oid, self.context)
            yield obj

    def __repr__(self):
        return '<%s len: %s>' % (self.__class__.__name__, len(self.oids))


class OIDSearchQuery(object):
    """Chainable query processor compatible with z3c.indexer IQuery items."""

    zope.interface.implements(interfaces.IOIDSearchQuery)

    _results = None

    def __init__(self, context, query=None):
        """Initialize with none or existing query."""
        self.context = context
        self.family = BTrees.family64
        res = None
        if query is not None:
            res = query.apply()
        if res is not None:
            self.results = self.family.IF.Set(res)

    @apply
    def results():
        """Ensure a empty result if None is given and allows to override
           existing results.
        """
        def get(self):
            if self._results is None:
                return self.family.IF.Set()
            return self._results
        def set(self, results):
            self._results = results
        return property(get, set)

    def apply(self):
        return self.results

    def searchResults(self, searchResultFactory=OIDResultSet):
        results = []
        if len(self.results) > 0:
            results = searchResultFactory(self.results, self.context)
        return results

    def Or(self, query):
        """Enhance search results. (union)

        The result will contain oids which exist in the existing result
        and/or in the result from te given query.
        """
        res = query.apply()
        if res:
            if len(self.results) == 0:
                # setup our first result if query=None was used in __init__
                self.results = self.family.IF.Set(res)
            else:
                self.results = self.family.IF.union(self.results, res)
        return self

    def And(self, query):
        """Restrict search results. (intersection)

        The result will only contain oids which exist in the existing
        result and in the result from the given query.
        """
        if len(self.results) == 0:
            # there is no need to do something if previous results is empty
            return self

        res = query.apply()
        if res:
            self.results = self.family.IF.intersection(self.results, res)
        # if given query is empty, means we have to return a empty result too!
        else:
            self.results = self.family.IF.Set()
        return self

    def Not(self, query):
        """Exclude search results. (difference)

        The result will only contain oids which exist in the existing
        result but do not exist in the result from te given query.

        This is faster if the existing result is small. But note, it get
        processed in a chain, results added after this query get added again.
        So probably you need to call this at the end of the chain.
        """
        if len(self.results) == 0:
            # there is no need to do something if previous results is empty
            return self

        res = query.apply()
        if res:
            self.results = self.family.IF.difference(self.results, res)
        return self
