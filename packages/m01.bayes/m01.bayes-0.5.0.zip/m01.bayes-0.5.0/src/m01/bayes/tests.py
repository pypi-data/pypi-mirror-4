###############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import unittest
import doctest

from m01.mongo import testing


def test_suite():
    suites = []
    append = suites.append

    # real mongo database tests using level 2 tests (--all)
    testNames = ['README.txt']
    for name in testNames:
        suite = unittest.TestSuite((
            doctest.DocFileSuite(name,
                setUp=testing.setUpStubMongoDB,
                tearDown=testing.tearDownStubMongoDB,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            ))
        suite.level = 2
        append(suite)

    # fake database tests
    testNames = ['README.txt']
    for name in testNames:
        append(
            doctest.DocFileSuite(name,
                setUp=testing.setUpFakeMongoDB,
                tearDown=testing.tearDownFakeMongoDB,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        )
    return unittest.TestSuite(suites)


if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
