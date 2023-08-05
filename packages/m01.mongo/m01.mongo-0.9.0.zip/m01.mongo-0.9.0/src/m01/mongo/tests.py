###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
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

    # real mongo database tests using m01.stub using level 2 tests (--all)
    testNames = ['README.txt',
                 'batching.txt',
                 'container.txt',
                 'geo.txt',
                 'object.txt',
                 'shared.txt',
                 'storage.txt',
                 ]
    for name in testNames:
        suite = unittest.TestSuite((
            doctest.DocFileSuite(name,
                setUp=testing.setUpStubMongoDB,
                tearDown=testing.tearDownStubMongoDB,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            ))
        suite.level = 2
        append(suite)

    # fake database tests. our fake database does not support ensure_index and
    # special prefixed commands like ($near). This menas we can't run all tests
    # with our fake database
    testNames = ['container.txt',
                 'object.txt',
                 'shared.txt',
                 'storage.txt',
                 ]
    for name in testNames:
        append(
            doctest.DocFileSuite(name,
                setUp=testing.setUpFakeMongoDB,
                tearDown=testing.tearDownFakeMongoDB,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        )
    append(
        doctest.DocFileSuite('testing.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
    )

    # return test suite
    return unittest.TestSuite(suites)


if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
