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
from zope.site import folder
from zope.keyreference.testing import SimpleKeyReference
from zope.app.testing import setup


###############################################################################
#
# Test Component
#
###############################################################################

class SiteStub(folder.Folder):
    """Sample site."""


###############################################################################
#
# setUp helper
#
###############################################################################

def setUp(test):
    test.globs = {'root': setup.placefulSetUp(True)}
    zope.component.provideAdapter(SimpleKeyReference)


def tearDown(test):
    setup.placefulTearDown()
