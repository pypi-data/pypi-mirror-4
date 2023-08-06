##############################################################################
#
# Copyright 2006 by Zope Foundation and Contributors
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
"""Tests for the package
"""
import doctest
import re
import unittest
from zope.site.testing import siteSetUp, siteTearDown
from zope.password.testing import setUpPasswordManagers
from zope.testing import renormalizing

checker = renormalizing.RENormalizing([
    # Python 3 unicode removed the "u".
    (re.compile("u('.*?')"),
     r"\1"),
    (re.compile('u(".*?")'),
     r"\1"),
    ])

def setUp(test):
    test.globs['root'] = siteSetUp(site=True)
    setUpPasswordManagers()

def tearDown(test):
    siteTearDown()


def test_suite():
    flags = doctest.NORMALIZE_WHITESPACE|\
            doctest.ELLIPSIS|\
            doctest.IGNORE_EXCEPTION_DETAIL
    return unittest.TestSuite((
        doctest.DocFileSuite(
                'README.txt',
                optionflags=flags, checker=checker,
                ),
        doctest.DocFileSuite(
                'generator/site.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=flags, checker=checker,
                ),
        doctest.DocFileSuite(
                'generator/intids.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=flags, checker=checker,
                ),
        doctest.DocFileSuite(
                'generator/pau.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=flags, checker=checker,
                ),
        doctest.DocFileSuite(
                'generator/principals.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=flags, checker=checker,
                ),
            ))
