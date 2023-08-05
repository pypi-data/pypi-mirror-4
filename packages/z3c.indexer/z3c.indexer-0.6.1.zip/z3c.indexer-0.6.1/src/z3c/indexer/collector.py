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

import threading
import transaction

import zope.interface

from z3c.indexer import interfaces


class IndexerCollector(object):
    """The collector stores pending indexer and their indexing state.
    
    These indexer get calculated and the relevant indexer get processed at
    the end of the transaction.
    """
    zope.interface.implements(interfaces.IIndexerCollector)

    def __init__(self, transaction):
        self.transaction = transaction
        self._pending = []
        self._prepared = False

    def addIndexer(self, name, indexer):
        """Index a value by it's id."""
        self._pending.append((name, indexer.oid, indexer, True))

    def addUnIndexer(self, name, indexer):
        # Since the oid is Lazy, we ensure by accessing it that the oid is
        # available after remove the object from the IntIds utility.
        self._pending.append((name, indexer.oid, indexer, False))

    def abort(self, transaction):
        self._checkTransaction(transaction)
        if self.transaction is not None:
            self.transaction = None
        self._pending = []
        self._prepared = False

    def tpc_begin(self, transaction):
        if self._prepared:
            raise TypeError('Already prepared')
        self._checkTransaction(transaction)
        self.transaction = transaction
        self._prepared = True

    def tpc_vote(self, transaction):
        """unify pending indexer calls.
        
        Some sample use cases are:
        
        index                     -> index
        index, index              -> index
        index, index, index       -> index

        unindex                   -> unindex
        index, unindex            -> unindex
        index, index, unindex     -> unindex

        The following usecases will work but should not happen:

        unindex, unindex          -> unindex (1)

        The following usecases will work but should not happen:
        
        unindex, index            -> works but should not happen (2)
        index, unindex, index     -> works but should not happen (2)
        
        (1) calling unindex two times without our indexer collector will end
        in a KeyError in IIntIds because of the already removed object. We 
        silently ignore this fact and just unindex the object once because it
        should never happen.

        (2) index after unindex means that the object get removed from the 
        IIntIds utility. This should never happen but will work. The following
        is going on in such a scenario. The last unindex will remove the oid
        from the indexes and the first index call will index the new oid in the
        relevant indexes.

        """
        self._checkTransaction(transaction)
        # find obsolate objects
        doIndex = []
        doUnIndex = []
        seen = {}
        # build a dict with final indexing states based on our chronological 
        # ordered (name, oid, indexer, state) list

        for name, oid, indexer, state in self._pending:
            seen[(name, oid, indexer.__class__)] = (indexer, state)

        for (name, oid, cls), (indexer, state) in seen.items():
            if state:
                indexer.doIndex()
            else:
                indexer.doUnIndex()
        self._pending = []

    def commit(self, transaction):
        pass

    def tpc_finish(self, transaction):
        pass

    def tpc_abort(self, transaction):
        self.abort(transaction)

    def _checkTransaction(self, transaction):
        if (self.transaction is not None and
            self.transaction is not transaction):
            raise TypeError("Transaction mismatch",
                            transaction, self.transaction)

    def sortKey(self):
        return str(id(self))


_collector = threading.local()

def get():
    """Returns a index collector

    Threading local provides a storage for our index collector. This will 
    ensure that we never use more then one collector in a transaction.
    """
    txn = transaction.manager.get()
    indexerCollector = getattr(_collector, 'z3cIndexerCollector', None)
    if indexerCollector is None:
        indexerCollector = IndexerCollector(txn)
        _collector.z3cIndexerCollector = indexerCollector
        txn.join(indexerCollector)
    elif txn != indexerCollector.transaction:
        # can happen in testing where we use more then one setUp, tearDown
        indexerCollector = IndexerCollector(txn)
        _collector.z3cIndexerCollector = indexerCollector
        txn.join(indexerCollector)
    return indexerCollector
