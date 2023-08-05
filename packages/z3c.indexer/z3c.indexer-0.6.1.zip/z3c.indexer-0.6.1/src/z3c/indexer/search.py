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

import zope.interface
import zope.component
from zope.intid.interfaces import IIntIds
from zope.index.interfaces import IIndexSort

from zc.catalog.index import FamilyProperty

from z3c.indexer import interfaces


class ResultSet:
    """Lazily accessed set of objects."""

    def __init__(self, uids, intids):
        self.uids = uids
        self.intids = intids

    def __len__(self):
        return len(self.uids)

    def __contains__(self, item):
        idx = self.intids.queryId(item)
        if idx is not None and idx in self.uids:
            return True
        else:
            return False

    def __getitem__(self, slice):
        start = slice.start
        stop = slice.stop
        if stop > len(self):
            stop = len(self)
        uids = self.uids
        getObject = self.intids.getObject
        return [getObject(uids[idx]) for idx in xrange(start, stop)]

    def __iter__(self):
        getObject = self.intids.getObject
        for uid in self.uids:
            obj = getObject(uid)
            yield obj

    def __repr__(self):
        return '<%s len: %s>' % (self.__class__.__name__, len(self.uids))


class SearchQuery(object):
    """Chainable query processor.

    Note: this search query is and acts as a chain. This means if you apply two
    query with the And method, the result will contain the intersection of both
    results. If you later add a query ithin the Or method to the chain the
    new result will contain items in the result we skipped with the And method
    before if the new query contains such (previous Not() filtered) items.
    """

    zope.interface.implements(interfaces.ISearchQuery)

    family = FamilyProperty()
    searchResultFactory = ResultSet
    _results = None

    def __init__(self, query=None, family=None):
        """Initialize with none or existing query."""
        res = None
        if query is not None:
            res = query.apply()
        if family is not None:
            self.family = family
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

    def searchResults(self, intids=None, searchResultFactory=None,
                        sort_index=None, reverse=False, limit=None):
        if searchResultFactory is None:
            searchResultFactory = self.searchResultFactory
        results = []
        if len(self.results) > 0:
            res = self.results
            if sort_index is not None:
                idx = zope.component.getUtility(interfaces.IIndex, name=sort_index)
                if not IIndexSort.providedBy(idx):
                    raise TypeError('Index %s does not implement sorting.' % sort_index)
                res = list(idx.sort(res, reverse, limit))
            else:
                if reverse or limit:
                    res = list(res)
                if reverse:
                    res.reverse()
                if limit:
                    del res[limit:]
            if intids is None:
                intids = zope.component.getUtility(IIntIds)
            results = searchResultFactory(res, intids)
        return results

    def Or(self, query):
        """Enhance search results. (union)

        The result will contain intids which exist in the existing result
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

        The result will only contain intids which exist in the existing
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

        The result will only contain intids which exist in the existing
        result but do not exist in the result from the given query.

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
