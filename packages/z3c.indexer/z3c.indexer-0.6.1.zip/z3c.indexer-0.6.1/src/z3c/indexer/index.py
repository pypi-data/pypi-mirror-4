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
from zope.container import contained
from zope.index.field import index as fieldindex
from zope.index.text import lexicon as lex
from zope.index.text import textindex
from BTrees.Length import Length
from zope.index.text import okapiindex

from zc.catalog import index as zcindex
from z3c.indexer import interfaces


class IndexMixin(object):
    """Index mixin class for indexes implementing zope.index.interfaces.IInjection"""

    def doIndex(self, oid, value):
        """Index a value by its object id."""
        self.index_doc(oid, value)

    def doUnIndex(self, oid):
        """Unindex a value by its object id."""
        self.unindex_doc(oid)


class TextIndex(IndexMixin, textindex.TextIndex, contained.Contained):
    """Text index based on zope.index.text.textindex.TextIndex"""

    zope.interface.implements(interfaces.ITextIndex)


class Lexicon64(lex.Lexicon):
    """Lexicon with long key support used by p01.oid."""

    def __init__(self, *pipeline):
        family64 = BTrees.family64
        #self._wids = OIBTree()  # word -> wid
        self._wids = family64.OI.BTree()
        #self._words = IOBTree() # wid -> word
        self._words = family64.IO.BTree()
        # wid 0 is reserved for words that aren't in the lexicon (OOV -- out
        # of vocabulary).  This can happen, e.g., if a query contains a word
        # we never saw before, and that isn't a known stopword (or otherwise
        # filtered out).  Returning a special wid value for OOV words is a
        # way to let clients know when an OOV word appears.
        self.wordCount = Length()
        self._pipeline = pipeline

    
class TextIndex64(TextIndex):
    """TextIndex with long key support used by p01.oid."""

    zope.interface.implements(interfaces.ITextIndex64)

    def __init__(self, lexicon=None, index=None):
        """Provisional constructor.

        This creates the lexicon and index if not passed in.
        """
        family64 = BTrees.family64
        if lexicon is None:
            lexicon = Lexicon64(lex.Splitter(), lex.CaseNormalizer(),
                lex.StopWordRemover())
        if index is None:
            index = okapiindex.OkapiIndex(lexicon, family64)
        self.lexicon = lexicon
        self.index = index


class FieldIndex(IndexMixin, fieldindex.FieldIndex,
    contained.Contained):
    """Field index based on zope.index.field.index.TextIndex
    
    Field index will use tuple in it's base apply method.
    """

    zope.interface.implements(interfaces.IFieldIndex)

    def applyEq(self, value):
        return self.apply((value, value))

    def applyNotEq(self, not_value):
        all = self.apply((None, None))
        r = self.apply((not_value, not_value))
        return self.family.IF.difference(all, r)

    def applyBetween(self, min_value, max_value, exclude_min=False,
        exclude_max=False):
        return self.apply((min_value, max_value))

    def applyGe(self, min_value, exclude_min=False):
        return self.apply((min_value, None))

    def applyLe(self, max_value, exclude_max=False):
        return self.apply((None, max_value))

    def applyIn(self, values):
        results = []
        for value in values:
            res = self.apply((value, value))
            # empty results
            if not res:
                continue
            results.append(res)

        if not results:
            # no applicable terms at all
            return self.family.IF.BTree()

        result = results.pop(0)
        for res in results:
            result = self.family.IF.union(result, res)
        return result


class ValueIndex(IndexMixin, zcindex.ValueIndex, contained.Contained):
    """Value index based on zc.catalog.index.ValueIndex"""

    zope.interface.implements(interfaces.IValueIndex)

    def applyEq(self, value):
        return self.apply({'any_of': (value,)})

    def applyNotEq(self, not_value):
        values = list(self.values())
        if not_value in values:
            values.remove(not_value)
        return self.apply({'any_of': values})

    def applyBetween(self, min_value, max_value, exclude_min, exclude_max):
        return self.apply(
            {'between': (min_value, max_value, exclude_min, exclude_max)})

    def applyGe(self, min_value, exclude_min=False):
        return self.apply({'between': (min_value, None, exclude_min, False)})

    def applyLe(self, max_value, exclude_max=False):
        return self.apply({'between': (None, max_value, False, exclude_max)})

    def applyIn(self, values):
        return self.apply({'any_of': values})

    def applyExtentAny(self, extent):
        return self.apply({'any': extent})

    def applyExtentNone(self, extent):
        return self.apply({'none': extent})


class SetIndex(IndexMixin, zcindex.SetIndex, contained.Contained):
    """Set index based on zc.catalog.index.SetIndex"""

    zope.interface.implements(interfaces.ISetIndex)

    def applyAnyOf(self, values):
        return self.apply({'any_of': values})

    def applyAllOf(self, values):
        return self.apply({'all_of': values})

    def applyBetween(self, min_value, max_value, exclude_min, exclude_max):
        self.tuple = (min_value, max_value, exclude_min, exclude_max)
        return self.apply({'between': self.tuple})

    def applyGe(self, min_value, exclude_min=False):
        self.tuple = (min_value, None, exclude_min, False)
        return self.apply({'between': self.tuple})

    def applyLe(self, max_value, exclude_max=False):
        self.tuple = (None, max_value, False, exclude_max)
        return self.apply({'between': self.tuple})

    def applyExtentAny(self, extent):
        return self.apply({'any': extent})

    def applyExtentNone(self, extent):
        return self.apply({'none': extent})
