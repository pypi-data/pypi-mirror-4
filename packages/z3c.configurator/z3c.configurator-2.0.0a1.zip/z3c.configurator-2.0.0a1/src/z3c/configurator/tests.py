##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
#############################################################################
"""Configurator Test Setup"""

__docformat__ = "reStructuredText"

import re
import unittest, doctest

from zope.component import testing
from zope.testing.renormalizing import RENormalizing


def setUp(test):
    testing.setUp(test)

def tearDown(test):
    testing.tearDown()


def test_suite():
    checker = RENormalizing((
            (re.compile("u'(.*?)'"), "'\\1'"),
            (re.compile("<type 'unicode'>"), "<class 'str'>"),
            (re.compile("zope.schema._bootstrapinterfaces.RequiredMissing"),
             "RequiredMissing"),
            (re.compile("zope.schema._bootstrapinterfaces.WrongType"),
             "WrongType"),
            ))
    return doctest.DocFileSuite(
        'README.txt',
        setUp=setUp, tearDown=tearDown, checker=checker,
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
