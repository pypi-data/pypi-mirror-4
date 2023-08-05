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
import zope.deferredimport

from transaction.interfaces import IDataManager
from zope.index.interfaces import IInjection
from zope.index.interfaces import IIndexSearch
from zope.index.interfaces import IStatistics
from zope.container.interfaces import IContained

NOVALUE = object()

# deprecated auto index subscribers
zope.deferredimport.deprecated(
    "IAutoIndexer will go away in 1.0.0 release. Use the new optimized "
    "intIdAddedEventDispatcher and intIdRemovedEventDispatcher subscribers.",
    IAutoIndexer = 'z3c.indexer._bbb:IAutoIndexer',
    IValueAutoIndexer = 'z3c.indexer._bbb:IValueAutoIndexer',
    IMultiAutoIndexer = 'z3c.indexer._bbb:IMultiAutoIndexer',
    )


class ISearchQuery(zope.interface.Interface):
    """Chainable search query."""

    def __init__(query=None, family=None):
        """Initialize with none or existing query."""

    results = zope.interface.Attribute("""List of initids.""")

    def apply():
        """Return iterable search result wrapper."""

    def searchResults(intids=None, searchResultFactory=None, sort_index=None, reverse=False, limit=None):
        """Returns an iterable search result objects.

        The IntIds utility can be specified for use in the ResulSet using the ``intids`` argument.
        
        The ``searchResultFactory`` argument can be used to specify a factory
        for the ResultSet object, returned by this method.
        
        The name of index to sort results with can be specified using the
        ``sort_index`` argument. The index should provide the
        zope.index.interfaces.IIndexSort interface. The optional ``reverse``
        and ``limit`` argument will be used by the index for efficient sorting.
        
        Though the ``limit`` and ``reverse`` arguments can be used without the
        ``sort_index``, it doesn't make much sense, because we can't guarantee
        any particular order in unsorted result set.

        """

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


# adapter based indexing concept
class IIndexer(zope.interface.Interface):
    """An Indexer knows how to index objects."""

    oid = zope.interface.Attribute("""IIntId of context.""")

    def doIndex():
        """Index the context in the relevant index."""

    def doUnIndex():
        """Unindex the context in the relevant index."""


class IValueIndexer(IIndexer):
    """An Indexer which knows the value used for indexing."""

    index = zope.interface.Attribute("""The named index utility.""")

    value = zope.interface.Attribute("""Value for context/index combination.""")


class IMultiIndexer(IIndexer):
    """Can be used a s base for index a object in more then one index."""

    def getIndex(indexName):
        """The named index utility getter method."""


# index base interface
class IIndex(zope.interface.Interface, IContained):
    """An Index marker interface."""

    def doIndex(obj, value):
        """Index a object."""

    def doUnIndex(obj):
        """Unindex a object."""

    def apply(query):
        """Simple apply method with single argument."""


# indexes
class ITextIndex(IIndex, IInjection, IIndexSearch, IStatistics):
    """Text index."""

    def apply(value):
        """Apply text query."""


class ITextIndex64(ITextIndex):
    """ITextIndex with family 64 BTree support."""


class IFieldIndex(IIndex):
    """Value index."""

    def applyEq(value):
        """Apply equals query."""

    def applyNotEq(not_value):
        """Apply not equals query."""

    def applyBetween(min_value, max_value, exclude_min=False,
        exclude_max=False):
        """Apply between query."""

    def applyGe(min_value, exclude_min=False):
        """Apply greater query."""

    def applyLe(max_value, exclude_max=False):
        """Apply less query."""

    def applyIn(values):
        """Apply in query."""


class IValueIndex(IIndex):
    """Value index."""

    def applyEq(value):
        """Apply equals query."""

    def applyNotEq(not_value):
        """Apply not equals query."""

    def applyBetween(min_value, max_value, exclude_min, exclude_max):
        """Apply between query."""

    def applyGe(min_value, exclude_min=False):
        """Apply greater query."""

    def applyLe(max_value, exclude_max=False):
        """Apply less query."""

    def applyIn(values):
        """Apply in query."""

    def applyExtentAny(extent):
        """Apply extent any query."""

    def applyExtentNone(extent):
        """Apply extent query."""


class ISetIndex(IIndex):
    """Value index."""

    def applyAnyOf(values):
        """Apply any of query."""

    def applyAllOf(values):
        """Apply all of query."""

    def applyBetween(min_value, max_value, exclude_min, exclude_max):
        """Apply between query."""

    def applyGe(min_value, exclude_min=False):
        """Apply greater query."""

    def applyLe(max_value, exclude_max=False):
        """Apply less query."""

    def applyExtentAny(extent):
        """Apply extent any query."""

    def applyExtentNone(extent):
        """Apply extent None query."""



# queries
class IQuery(zope.interface.Interface):
    """Search query."""

    def apply():
        """Apply query with predefined query value."""


class ITextQuery(IQuery):
    """Text index query."""

    def __init__(indexOrName, value):
        """Query signature."""


class IEqQuery(IQuery):
    """Equal query."""

    def __init__(indexOrName, value):
        """Query signature."""


class INotEqQuery(IQuery):
    """Not equal query."""

    def __init__(indexOrName, not_value):
        """Query signature."""


class IBetweenQuery(IQuery):
    """Between query."""

    def __init__(indexOrName, min_value, max_value):
        """Query signature."""


class IGeQuery(IQuery):
    """Greater query."""

    def __init__(indexOrName, min_value):
        """Query signature."""


class ILeQuery(IQuery):
    """Less query."""

    def __init__(indexOrName, max_value):
        """Query signature."""


class IInQuery(IQuery):
    """In query."""

    def __init__(indexOrName, values):
        """Query signature."""


class IAnyOfQuery(IQuery):
    """AnyOf query.

    The result will be the docids whose values contain any of the given values.
    """

    def __init__(indexOrName, values):
        """Query signature."""


class IAllOfQuery(IQuery):
    """AllOf query.

    The result will be the docids whose values contain all of the given values.
    """

    def __init__(indexOrName, values):
        """Query signature."""


class IExtentAnyQuery(IQuery):
    """ExtentAny query."""

    def __init__(indexOrName, values):
        """Query signature."""


class IExtentNoneQuery(IQuery):
    """ExtentNone query."""

    def __init__(indexOrName, values):
        """Query signature."""


# transaction based indexing concept
class IIndexerCollector(IDataManager):
    """Collects IIndexer which get processed at the end of the transaction."""

    def addIndexer(obj):
        """Add an object indexer."""

    def addUnIndexer(obj):
        """Add an object un-indexer."""
