##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
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

import unittest
import doctest

#from m01.mongo import testing

from m01.logger import testing


def test_suite():
    return unittest.TestSuite([
        # real mongodb test setup
        doctest.DocFileSuite('README.txt',
            setUp=testing.setUpMongoDB,
            tearDown=testing.tearDownMongoDB,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        doctest.DocFileSuite('capacity.txt',
            setUp=testing.setUpMongoDBOverrideCapacity,
            tearDown=testing.tearDownMongoDB,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ])


if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
