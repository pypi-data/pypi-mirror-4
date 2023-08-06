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
import unittest
from zope.app.testing.setup import placefulSetUp, placefulTearDown


def setUp(test):
    root = placefulSetUp(site=True)
    test.globs['root'] = root


def tearDown(test):
    placefulTearDown()


def test_suite():

    return unittest.TestSuite((
        doctest.DocFileSuite(
                'README.txt',
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                ),
        doctest.DocFileSuite(
                'generator/site.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                ),
        doctest.DocFileSuite(
                'generator/intids.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                ),
        doctest.DocFileSuite(
                'generator/pau.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                ),
        doctest.DocFileSuite(
                'generator/principals.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                ),
            ))
