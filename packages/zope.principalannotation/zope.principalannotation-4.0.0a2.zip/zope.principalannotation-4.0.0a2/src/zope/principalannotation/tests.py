##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Principal Annotation Tests
"""
import unittest
from zope.component import provideAdapter
from zope.testing import doctest
from zope.interface import Interface
from zope.security.interfaces import IPrincipal
from zope.site.testing import siteSetUp, siteTearDown

from zope.principalannotation.utility import annotations

def setUp(test):
    site = siteSetUp(site=True)
    test.globs['root'] = site
    provideAdapter(annotations)
    provideAdapter(annotations, (IPrincipal, Interface))

def tearDown(test):
    siteTearDown()

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.ELLIPSIS)
        ))
