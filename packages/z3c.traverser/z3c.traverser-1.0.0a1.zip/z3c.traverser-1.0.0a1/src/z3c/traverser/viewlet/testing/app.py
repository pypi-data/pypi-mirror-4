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
"""Sample Application
"""
from zope.viewlet import interfaces
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile


class IMyManager(interfaces.IViewletManager):
    """Viewlet manager"""

class MyViewlet(object):

    def upate(self):
        pass

    def render(self):
        return '<div><a href="%s">My Viewlet</a></div>' % \
               absoluteURL(self, self.request)


class IOuterManager(interfaces.IViewletManager):
    """Outer viewlet manager"""


class IInnerManager(interfaces.IViewletManager):
    """Inner viewlet manager"""


class IMostInnerManager(interfaces.IViewletManager):
    """Most inner viewlet manager"""


class OuterViewlet(object):

    template = ViewPageTemplateFile('outer.pt')

    def upate(self):
        pass

    def render(self):
        return self.template()


class InnerViewlet(object):

    template = ViewPageTemplateFile('inner.pt')

    def upate(self):
        pass

    def render(self):
        return self.template()


class MostInnerViewlet(object):

    def upate(self):
        pass

    def render(self):
        return '<div><a href="%s">Most inner viewlet</a></div>' % \
               absoluteURL(self, self.request)
