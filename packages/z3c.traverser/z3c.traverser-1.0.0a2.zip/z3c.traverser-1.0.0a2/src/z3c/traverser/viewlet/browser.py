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
"""Viewlet Traverser Browser Supprot
"""
import zope.component
from zope import event
from zope.contentprovider.interfaces import BeforeUpdateEvent
from zope.publisher.browser import BrowserView
from zope.security.proxy import removeSecurityProxy
from zope.traversing.browser import absoluteurl

from z3c.traverser._compat import quote, unquote

class ViewletAbsoluteURL(absoluteurl.AbsoluteURL):

    def __str__(self):
        context = removeSecurityProxy(self.context)
        request = self.request

        # The application URL contains all the namespaces that are at the
        # beginning of the URL, such as skins, virtual host specifications and
        # so on.

        container = getattr(context, 'manager', None)
        if container is None:
            raise TypeError(absoluteurl._insufficientContext)
        url = str(zope.component.getMultiAdapter((container, request),
                                                 name='absolute_url'))
        name = self._getContextName(context)
        if name is None:
            raise TypeError(absoluteurl._insufficientContext)

        if name:
            url += '/' + quote(name.encode('utf-8'), absoluteurl._safe)

        return url

    def _getContextName(self, context):
        name = getattr(context, '__name__', None)
        return u'++viewlet++' + name


    __call__ = __str__

class ViewletManagerAbsoluteURL(absoluteurl.AbsoluteURL):

    def __str__(self):
        context = self.context
        request = self.request

        container = getattr(context, '__parent__', None)
        if container is None:
            raise TypeError(absoluteurl._insufficientContext)
        url = str(zope.component.getMultiAdapter((container, request),
                                                 name='absolute_url'))
        name = self._getContextName(context)
        if name is None:
            raise TypeError(absoluteurl._insufficientContext)

        if name:
            url += '/' + quote(name.encode('utf-8'), absoluteurl._safe)

        return url


    def _getContextName(self, context):
        name = getattr(context, '__name__', None)
        return u'++manager++' + name

    __call__ = __str__

class ViewletView(BrowserView):

    def __call__(self):
        event.notify(BeforeUpdateEvent(self.context, self.request))
        self.context.update()
        return self.context.render()
