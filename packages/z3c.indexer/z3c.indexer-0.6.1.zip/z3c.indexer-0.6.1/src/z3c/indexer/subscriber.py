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
"""Indexing pattern

Configure one of this different indexing pattern or use the 
z3c.indexer.indexer.index method explicit if needed.

$Id:$
"""
__docformat__ = "reStructuredText"

import zope.component
import zope.deferredimport
import zope.lifecycleevent.interfaces

import zope.intid.interfaces
from zope.intid.interfaces import IIntIds

from z3c.indexer import interfaces
from z3c.indexer import collector


###############################################################################
#
# Auto indexing strategy
#
#
# The first indexing pattern offers a python method called index which will
# lookup one or more object IIndexer adapters which will index the object based 
# on this IIndexer adapters. In the initial release we offered subscribers
# for this indexing methods. This subscribers will get deprecated in the
# release 1.0.0 because this indexing strategy is to slow because it will
# index one object more then one time if more then one time if too much events
# are involved. e.g. adding more then one object.
#
# The auto indexer implementation will be removed in 1.0.0 release.
#
###############################################################################
# deprecated auto index subscribers
zope.deferredimport.deprecated(
    "IAutoIndexer will go away in 1.0.0 release. Implement IIndexerSubscriber "
    "and use them within the new intIdAddedEventDispatcher and "
    "intIdRemovedEventDispatcher subscribers.",
    autoIndexSubscriber = 'z3c.indexer._bbb:autoIndexSubscriber',
    autoUnindexSubscriber = 'z3c.indexer._bbb:autoUnindexSubscriber',
    )


###############################################################################
#
# Unified indexing strategy
#
#
# The second indexing pattern registers indexer with a transaction data manager.
# This allows us to filter multiple index calls and only use the latest which
# is very useful because object modified event will force to index an object
# more then one time during a transaction.
#
###############################################################################
# object added
@zope.component.adapter(zope.intid.interfaces.IIntIdAddedEvent)
def intIdAddedEventDispatcher(event):
    """Event subscriber to dispatch IntIdAddedEvent to IIndexer adapters.

    This event subscriber allows to use IIndexer adapters and collects them
    in the transaction data manager. At the end of the transaction the different
    registered adapters get calculated and only relevant indexer get processed.
    
    This will ensure that we never process an indexer more then one time per 
    transaction.
    """
    adapters = zope.component.getAdapters((event.object,), interfaces.IIndexer)
    if adapters:
        # collect indexer
        iCollector = collector.get()
        for name, indexer in adapters:
            iCollector.addIndexer(name, indexer)


# object modified
@zope.component.adapter(zope.lifecycleevent.interfaces.IObjectModifiedEvent)
def objectModifiedDispatcher(event):
    """Event subscriber to dispatch IObjectModifiedEvent to interested adapters.
    """
    adapters = zope.component.getAdapters((event.object,), interfaces.IIndexer)
    if adapters:
        # collect indexer
        iCollector = collector.get()
        for name, indexer in adapters:
            iCollector.addIndexer(name, indexer)


# object removed
@zope.component.adapter(zope.intid.interfaces.IIntIdRemovedEvent)
def intIdRemovedEventDispatcher(event):
    """Event subscriber to dispatch IIntIdRemovedEvent to interested adapters.

    This event subscriber allows to use subscription adapters for 
    (object, IIntIdRemovedEvent) which reduces simple (IIntIdRemovedEvent)
    subscription adapter calls and makes the indexing story more explicit.
    """
    adapters = zope.component.getAdapters((event.object,), interfaces.IIndexer)
    if adapters:
        # collect indexer
        iCollector = collector.get()
        for name, indexer in adapters:
            iCollector.addUnIndexer(name, indexer)
