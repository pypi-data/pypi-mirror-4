##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Traverser StakcInfo Tests
"""
import doctest
import re
import unittest
import zope.site.testing
import zope.traversing.testing
from zope.app.wsgi.testlayer import BrowserLayer
from zope.component import provideAdapter
from zope.interface import Interface
from zope.publisher.interfaces.http import IHTTPRequest
from zope.testing import renormalizing

import z3c.traverser.stackinfo
from z3c.traverser.stackinfo.traversing import UnconsumedURL

checker = renormalizing.RENormalizing([
    # Python 3 unicode removed the "u".
    (re.compile("u('.*?')"),
     r"\1"),
    (re.compile('u(".*?")'),
     r"\1"),
    ])

def setUp(test):
    root = zope.site.testing.siteSetUp(True)
    zope.traversing.testing.setUp()
    test.globs['root'] = root
    provideAdapter(UnconsumedURL, (Interface, IHTTPRequest), Interface,
                   name='unconsumed_url')

def tearDown(test):
    zope.site.testing.siteTearDown()

browser_layer = BrowserLayer(z3c.traverser.stackinfo, 'ftesting.zcml')

def setUpBrowser(test):
    test.globs['wsgi_app'] = browser_layer.make_wsgi_app()

def test_suite():
    flags = doctest.NORMALIZE_WHITESPACE|\
            doctest.ELLIPSIS|\
            doctest.IGNORE_EXCEPTION_DETAIL
    suite = unittest.TestSuite((
            doctest.DocFileSuite(
                'README.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=flags, checker=checker),
            ))
    browser_suite = doctest.DocFileSuite(
        'BROWSER.txt', setUp=setUpBrowser, optionflags=flags, checker=checker)
    browser_suite.layer = browser_layer
    suite.addTest(browser_suite)
    return suite
