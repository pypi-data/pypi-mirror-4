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
"""Stack Info Consumer.
"""
from zope import interface, component
from zope.publisher.interfaces.browser import IBrowserRequest

from z3c.traverser.stackinfo import interfaces, traversing

@component.adapter(IBrowserRequest)
@interface.implementer(interfaces.ITraversalStackInfo)
def requestTraversalStackInfo(request):
    cons = request.annotations.get(traversing.CONSUMERS_ANNOTATION_KEY, [])
    return TraversalStackInfo(cons)

@interface.implementer(interfaces.ITraversalStackInfo)
class TraversalStackInfo(tuple):
    pass

@interface.implementer(interfaces.ITraversalStackConsumer)
class BaseConsumer(object):

    arguments = ()
    __name__ = None

    def __init__(self, context, request):
        self.context=context
        self.request=request

    def consume(self):
        stack = self.request.getTraversalStack()
        self.__name__ = stack.pop()
        consumed = [self.__name__]
        for name in self.arguments:
            v = stack.pop()
            consumed.append(v)
            setattr(self, name, v)
        self.request.setTraversalStack(stack)
        return consumed

    def __repr__(self):
        return '<%s named %r>' % (self.__class__.__name__,
                                  self.__name__)


