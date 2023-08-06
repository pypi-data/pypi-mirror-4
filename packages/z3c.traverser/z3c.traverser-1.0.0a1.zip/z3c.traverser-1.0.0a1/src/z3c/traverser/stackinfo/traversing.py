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
"""Stack Info Traverser.
"""
from __future__ import absolute_import

from zope import component
from zope.proxy import sameProxiedObjects
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import NotFound
from zope.traversing.browser.absoluteurl import absoluteURL

from z3c.traverser._compat import quote, unquote
from . import interfaces

CONSUMERS_ANNOTATION_KEY='z3c.traverser.consumers'
CONSUMED_ANNOTATION_KEY='z3c.traverser.consumed'

def getStackConsumers(context, request):
    """consumes the stack"""
    vhStack = VHStack(request)
    while True:
        vhStack.prepare()
        stack = request.getTraversalStack()
        if not stack:
            break
        name = stack[-1]
        consumer = component.queryMultiAdapter(
                        (context, request),
                        interface=interfaces.ITraversalStackConsumer,
                        name=name)
        if consumer is None:
            break
        try:
            consumer.consume()
        except IndexError:
            raise NotFound(context, name, request)
        vhStack.reset()
        yield (name, consumer)
    vhStack.reset()


def applyStackConsumers(context, request):
    if CONSUMED_ANNOTATION_KEY not in request.annotations:
        request.annotations[CONSUMED_ANNOTATION_KEY] = []
        request.annotations[CONSUMERS_ANNOTATION_KEY] = []
    else:
        for obj, consumed in request.annotations[CONSUMED_ANNOTATION_KEY]:
            if sameProxiedObjects(obj, context):
                return
    orgStack = request.getTraversalStack()
    cons = [cons for name, cons in getStackConsumers(
        context, request)]
    newStack = request.getTraversalStack()
    if newStack != orgStack:
        consumed = request.annotations[CONSUMED_ANNOTATION_KEY]
        numItems = len(orgStack)-len(newStack)
        vhStack = VHStack(request)
        vhStack.prepare()
        stack = request.getTraversalStack()
        items = orgStack[len(stack):len(stack)+numItems]
        vhStack.reset()
        items.reverse()
        consumed.append((context, items))
    request.annotations[CONSUMERS_ANNOTATION_KEY].extend(cons)


def _encode(v, _safe='@+'):
    return quote(v.encode('utf-8'), _safe)


def unconsumedURL(context, request):
    url = absoluteURL(context, request)
    consumed = request.annotations.get(CONSUMED_ANNOTATION_KEY)
    if not consumed:
        return url
    inserts = []
    for obj, names in consumed:
        if obj is context:
            # only calculate once
            objURL = url
        else:
            objURL = absoluteURL(obj, request)
        if not url.startswith(objURL):
            # we are further down
            break
        names = '/' + '/'.join(map(_encode, names))
        inserts.append((len(objURL), names))

    offset = 0
    for i, s in inserts:
        oi = i + offset
        pre = url[:oi]
        post = url[oi:]
        url = pre + s + post
        offset += len(s)
    return url

class UnconsumedURL(BrowserView):

    def __unicode__(self):
        return unquote(self.__str__()).decode('utf-8')

    def __str__(self):
        return unconsumedURL(self.context, self.request)

    __call__ = __str__

class VHStack(object):
    """Helper class to work around the special case with virtual hosts"""

    def __init__(self, request):
        self.request = request
        self.vh = []

    def prepare(self):
        if not self.vh:
            stack = self.request.getTraversalStack()
            if not stack:
                return
            name = stack[-1]
            if name.startswith('++vh++'):
                while True:
                    self.vh.append(stack.pop())
                    if name == '++':
                        break
                    if not stack:
                        break
                    name = stack[-1]
                # set stack without virtual host entries
                self.request.setTraversalStack(stack)

    def reset(self):
        if self.vh:
            stack = self.request.getTraversalStack()
            while self.vh:
                stack.append(self.vh.pop())
            self.request.setTraversalStack(stack)

