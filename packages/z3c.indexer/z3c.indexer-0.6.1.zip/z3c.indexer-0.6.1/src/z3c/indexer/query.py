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

import zope.component
from z3c.indexer import interfaces


class QueryMixin(object):
    """Index query."""

    def __init__(self, indexOrName):
        if isinstance(indexOrName, basestring):
            self.index = zope.component.getUtility(interfaces.IIndex,
                name=indexOrName)
        else:
            # indexOrName is a index
            self.index = indexOrName


class TextQuery(QueryMixin):
    """Text query."""

    zope.interface.implements(interfaces.ITextQuery)

    def __init__(self, indexOrName, value):
        super(TextQuery, self).__init__(indexOrName)
        self.value = value

    def apply(self):
        return self.index.apply(self.value)


class Eq(QueryMixin):
    """Equal query."""

    zope.interface.implements(interfaces.IEqQuery)

    def __init__(self, indexOrName, value):
        assert value is not None
        super(Eq, self).__init__(indexOrName)
        self.value = value

    def apply(self):
        return self.index.applyEq(self.value)


class NotEq(QueryMixin):
    """Not equal query."""

    zope.interface.implements(interfaces.INotEqQuery)

    def __init__(self, indexOrName, value):
        assert value is not None
        super(NotEq, self).__init__(indexOrName)
        self.value = value

    def apply(self):
        return self.index.applyNotEq(self.value)


class Between(QueryMixin):
    """Between query."""

    zope.interface.implements(interfaces.IBetweenQuery)

    def __init__(self, indexOrName, min_value, max_value, exclude_min=False,
        exclude_max=False):
        super(Between, self).__init__(indexOrName)
        self.min_value = min_value
        self.max_value = max_value
        self.exclude_min = exclude_min
        self.exclude_max = exclude_max

    def apply(self):
        return self.index.applyBetween(self.min_value, self.max_value,
            self.exclude_min, self.exclude_max)


class Ge(QueryMixin):
    """Greater (or equal) query."""

    zope.interface.implements(interfaces.IGeQuery)

    def __init__(self, indexOrName, min_value, exclude_min=False):
        super(Ge, self).__init__(indexOrName)
        self.min_value = min_value
        self.exclude_min = exclude_min

    def apply(self):
        return self.index.applyGe(self.min_value, self.exclude_min)


class Le(QueryMixin):
    """Less (or equal) query."""

    zope.interface.implements(interfaces.ILeQuery)

    def __init__(self, indexOrName, max_value, exclude_max=False):
        super(Le, self).__init__(indexOrName)
        self.max_value = max_value
        self.exclude_max = exclude_max

    def apply(self):
        return self.index.applyLe(self.max_value, self.exclude_max)


class In(QueryMixin):
    """In query."""

    zope.interface.implements(interfaces.IInQuery)

    def __init__(self, indexOrName, values):
        super(In, self).__init__(indexOrName)
        self.values = values

    def apply(self):
        return self.index.applyIn(self.values)


class AnyOf(QueryMixin):
    """Any of query.

    The result will be the docids whose values contain any of the given values.
    """

    zope.interface.implements(interfaces.IAnyOfQuery)

    def __init__(self, indexOrName, values):
        super(AnyOf, self).__init__(indexOrName)
        self.values = values

    def apply(self):
        return self.index.applyAnyOf(self.values)


class AllOf(QueryMixin):
    """Any of query.

    The result will be the docids whose values contain all of the given values.
    """

    zope.interface.implements(interfaces.IAllOfQuery)

    def __init__(self, indexOrName, values):
        super(AllOf, self).__init__(indexOrName)
        self.values = values

    def apply(self):
        return self.index.applyAllOf(self.values)


class ExtentAny(QueryMixin):
    """ExtentAny query."""

    zope.interface.implements(interfaces.IExtentAnyQuery)

    def __init__(self, indexOrName, extent):
        super(ExtentAny, self).__init__(indexOrName)
        self.extent = extent

    def apply(self):
        return self.index.applyExtentAny(self.extent)


class ExtentNone(QueryMixin):
    """ExtentNone query."""

    zope.interface.implements(interfaces.IExtentNoneQuery)

    def __init__(self, indexOrName, extent):
        super(ExtentNone, self).__init__(indexOrName)
        self.extent = extent

    def apply(self):
        return self.index.applyExtentNone(self.extent)
