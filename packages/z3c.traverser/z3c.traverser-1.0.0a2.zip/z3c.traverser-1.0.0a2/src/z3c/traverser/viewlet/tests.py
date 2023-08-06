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
"""Viewlet Traverser Tests
"""
import doctest
import unittest

import zope.site.testing
import zope.traversing.testing
from zope.app.wsgi.testlayer import BrowserLayer
from zope.traversing.browser import AbsoluteURL, SiteAbsoluteURL
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.interfaces import IContainmentRoot
from zope.traversing.testing import browserView

import z3c.traverser.viewlet

def setUp(test):
    root = zope.site.testing.siteSetUp(True)
    zope.traversing.testing.setUp()
    test.globs['root'] = root

    browserView(None, 'absolute_url', AbsoluteURL)
    browserView(IContainmentRoot, 'absolute_url', SiteAbsoluteURL)
    browserView(None, '', AbsoluteURL, providing=IAbsoluteURL)
    browserView(IContainmentRoot, '', SiteAbsoluteURL, providing=IAbsoluteURL)

def tearDown(test):
    zope.site.testing.siteTearDown()

browser_layer = BrowserLayer(z3c.traverser.viewlet, 'ftesting.zcml')

def setUpBrowser(test):
    test.globs['wsgi_app'] = browser_layer.make_wsgi_app()

def test_suite():
    flags = doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
    suite = unittest.TestSuite((
            doctest.DocFileSuite(
                'README.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=flags),
            ))
    browser_suite = doctest.DocFileSuite(
        'BROWSER.txt', setUp=setUpBrowser, optionflags=flags)
    browser_suite.layer = browser_layer
    suite.addTest(browser_suite)
    return suite
