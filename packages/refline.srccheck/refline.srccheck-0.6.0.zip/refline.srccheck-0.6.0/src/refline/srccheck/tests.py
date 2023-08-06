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

$Id: tests.py 130168 2013-03-26 23:51:48Z alga $
"""
import unittest
import doctest
import re

from zope.testing.renormalizing import RENormalizing


def test_suite():
    return doctest.DocFileSuite(
        'README.txt',
        optionflags=doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS,
        checker=RENormalizing([(re.compile(u"u':'"), "':'")])
        )
