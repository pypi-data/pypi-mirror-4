##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
"""Tests
"""
import doctest
import itertools
import re
import unittest
import zope.component
from zope.configuration import xmlconfig
from zope.component import testing
from zope.testing import renormalizing

import z3c.template.template

checker = renormalizing.RENormalizing([
    # Python 3 unicode removed the "u".
    #(re.compile("u('.*?')"),
    # r"\1"),
    #(re.compile('u(".*?")'),
    # r"\1"),
    # Python 3 adds module name to exceptions.
    (re.compile("zope.interface.interfaces.ComponentLookupError"),
     r"ComponentLookupError"),
    ])

try:
    import z3c.ptcompat
except ImportError:
    Z3CPT_AVAILABLE = False
else:
    Z3CPT_AVAILABLE = True


def setUp(test):
    testing.setUp(test)
    # Traversal Setup
    from zope.traversing.testing import setUp
    setUp()
    test.globs['root'] = object()

def tearDown(test):
    testing.tearDown(test)

def setUpZPT(suite):
    setUp(suite)

def setUpZ3CPT(suite):
    setUp(suite)
    import z3c.pt
    import z3c.ptcompat
    xmlconfig.XMLConfig('configure.zcml', z3c.pt)()
    xmlconfig.XMLConfig('configure.zcml', z3c.ptcompat)()

    # We have to cook this template explicitly, because it's a module
    # global.
    from z3c.template.template import Macro
    Macro.wrapper._cook()


def test_suite():
    setups = (setUpZPT,)
    if Z3CPT_AVAILABLE:
        setups += (setUpZ3CPT,)
    tests = ((
        doctest.DocFileSuite('README.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker,
            ),
        doctest.DocFileSuite('zcml.txt', setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker,
            ),
        ) for setUp in setups)

    return unittest.TestSuite(itertools.chain(*tests))
