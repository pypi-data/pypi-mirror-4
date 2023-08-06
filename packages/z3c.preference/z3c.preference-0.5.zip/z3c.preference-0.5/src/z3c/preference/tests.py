##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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

import doctest
import z3c.preference.testing
import zope.component.testing
import zope.testing.module


def setUp(test):
    zope.testing.module.setUp(test, 'z3c.preference.README')
    zope.testing.module.setUp(test, 'z3c.preference.categories')


def tearDown(test):
    zope.testing.module.tearDown(test)


def test_suite():
    suite = doctest.DocFileSuite(
        'README.txt',
        'categories.txt',
        setUp=setUp,
        tearDown=tearDown,
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = z3c.preference.testing.Layer
    return suite
