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
from zope.intid.interfaces import IIntIdAddedEvent
from zope.intid.interfaces import IIntIdRemovedEvent

from z3c.indexer import interfaces
from z3c.indexer import indexer


# Remove in 1.0.0 release
class IAutoIndexer(zope.interface.Interface):
    """Auto indexer adapter get called by the auto indexer subscriber."""

    oid = zope.interface.Attribute("""IIntId of context.""")

    def doIndex():
        """Index the context in the relevant index."""

    def doUnIndex():
        """Unindex the context in the relevant index."""


class IValueAutoIndexer(IAutoIndexer):
    """Value (auto) indexer."""

    index = zope.interface.Attribute("""The named index utility.""")

    value = zope.interface.Attribute("""Value for context/index combination.""")


class IMultiAutoIndexer(IAutoIndexer):
    """Multi (auto) indexer"""

    def getIndex(indexName):
        """The named index utility getter method."""


# implicit indexing pattern (generic)
# IAutoIndexer adapter
@zope.component.adapter(IIntIdAddedEvent)
def autoIndexSubscriber(event):
    """Index all objects which get added to the intids utility."""
    adapters = zope.component.getAdapters((event.object,),
        interfaces.IAutoIndexer)
    for name, adapter in adapters:
        adapter.doIndex()


# IAutoIndexer adapter
@zope.component.adapter(IIntIdRemovedEvent)
def autoUnindexSubscriber(event):
    """Unindex all objects which get added to the intids utility."""
    adapters = zope.component.getAdapters((event.object,),
        interfaces.IAutoIndexer)
    for name, adapter in adapters:
        adapter.doUnIndex()


class ValueAutoIndexer(indexer.ValueIndexerBase):
    """Value (auto) indexer implementation."""

    zope.interface.implements(interfaces.IValueAutoIndexer)


class MultiAutoIndexer(indexer.MultiIndexerBase):
    """Can be used as base for index a object in more then one index."""

    zope.interface.implements(interfaces.IMultiAutoIndexer)
