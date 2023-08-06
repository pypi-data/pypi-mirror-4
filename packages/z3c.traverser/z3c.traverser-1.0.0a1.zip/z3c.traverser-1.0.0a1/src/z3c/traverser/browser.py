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
"""Pluggable Browser Traverser
"""
from zope.interface import implementer
from zope.publisher.defaultview import getDefaultViewName
from zope.publisher.interfaces.browser import IBrowserPublisher

from z3c.traverser.traverser import PluggableTraverser

@implementer(IBrowserPublisher)
class PluggableBrowserTraverser(PluggableTraverser):

    def browserDefault(self, request):
        """See zope.publisher.browser.interfaces.IBrowserPublisher"""
        view_name = getDefaultViewName(self.context, request)
        view_uri = "@@%s" % view_name
        return self.context, (view_uri,)
