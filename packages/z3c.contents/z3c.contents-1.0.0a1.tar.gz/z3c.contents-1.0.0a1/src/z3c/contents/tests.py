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

import re
import unittest
from zope.testing import doctest

try:
    from zope.app.testing import functional
    HAVE_FTESTS = True
except ImportError:
    HAVE_FTESTS = False

from zope.testing.renormalizing import RENormalizing

from z3c.contents import testing


optionflags = (doctest.NORMALIZE_WHITESPACE
               | doctest.ELLIPSIS
               | doctest.REPORT_NDIFF)

TestLayer = None # shut up pyflakes warning
if HAVE_FTESTS:
    functional.defineLayer('TestLayer', 'ftesting.zcml',
                           allow_teardown=True)


def ftest_suite():
    if not HAVE_FTESTS:
        return unittest.TestSuite()
    docTest = functional.FunctionalDocFileSuite('BROWSER.txt',
        setUp=testing.doctestSetUp, tearDown=testing.doctestTearDown,
        optionflags=optionflags)
    docTest.layer = TestLayer
    return docTest


def test_suite():
    checker = RENormalizing((
            (re.compile("u'(.*?)'"), "'\\1'"),
            ))
    return unittest.TestSuite([
        doctest.DocFileSuite('README.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=optionflags, checker=checker,
            ),
        ftest_suite(),
    ])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
