##############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH and Contributors.
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
$Id: tests.py 3487 2012-11-23 04:02:48Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import doctest
import unittest

import z3c.form.testing


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            setUp=z3c.form.testing.setUp,
            tearDown=z3c.form.testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        doctest.DocFileSuite('util.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
