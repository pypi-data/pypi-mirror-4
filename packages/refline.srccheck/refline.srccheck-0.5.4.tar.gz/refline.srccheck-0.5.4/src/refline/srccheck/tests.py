##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
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

$Id: tests.py 124883 2012-04-02 14:17:23Z adamg $
"""
import unittest
import doctest


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS,
            ),
        ))
