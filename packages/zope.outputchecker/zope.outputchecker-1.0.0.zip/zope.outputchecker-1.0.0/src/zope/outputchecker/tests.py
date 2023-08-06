##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
""" Test the event system
"""
import doctest
import re
import unittest

from .checker import OutputChecker

CHECKER = OutputChecker(
    patterns =(
        (re.compile("Good morning (.*)!"), r"Guten Tag \1!"),
    )
)

def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite('README.txt', checker=CHECKER)
        ))
