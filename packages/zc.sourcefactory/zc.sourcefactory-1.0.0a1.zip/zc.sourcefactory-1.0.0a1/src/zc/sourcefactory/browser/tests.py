##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
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
"""Unit tests
"""
import doctest
import unittest

from zc.sourcefactory.tests import setUp, tearDown, checker

def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                'token.txt', setUp=setUp, tearDown=tearDown,
                checker=checker, optionflags=doctest.ELLIPSIS),
            doctest.DocFileSuite(
                'README.txt', setUp=setUp, tearDown=tearDown,
                checker=checker, optionflags=doctest.ELLIPSIS),
            ))
