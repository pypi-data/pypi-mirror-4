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
"""Pluggable Traverser Implementation
"""
from zope.interface import implementer
from zope.component import subscribers, queryAdapter, queryMultiAdapter
from zope.publisher.interfaces import NotFound

from z3c.traverser import interfaces

_marker = object()


@implementer(interfaces.IPluggableTraverser)
class BasePluggableTraverser(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        # Look at all the traverser plugins, whether they have an answer.
        for traverser in subscribers((self.context, request),
                                     interfaces.ITraverserPlugin):
            try:
                return traverser.publishTraverse(request, name)
            except NotFound:
                pass

        raise NotFound(self.context, name, request)


class PluggableTraverser(BasePluggableTraverser):
    """Generic Pluggable Traverser."""

    def publishTraverse(self, request, name):
        try:
            return super(PluggableTraverser, self).publishTraverse(
                request, name)
        except NotFound:
            pass

        # The traversers did not have an answer, so let's see whether it is a
        # view.
        view = queryMultiAdapter((self.context, request), name=name)
        if view is not None:
            return view

        raise NotFound(self.context, name, request)


@implementer(interfaces.ITraverserPlugin)
class NameTraverserPlugin(object):
    """Abstract class that traverses an object by name."""

    traversalName = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        if name == self.traversalName:
            return self._traverse(request, name)
        raise NotFound(self.context, name, request)

    def _traverse(self, request, name):
        raise NotImplemented('Method must be implemented by subclasses.')


class NullTraverserPluginTemplate(NameTraverserPlugin):
    """Traverse to an adapter by name."""

    def _traverse(self, request, name):
        return self.context


def NullTraverserPlugin(traversalName):
    return type('NullTraverserPlugin', (NullTraverserPluginTemplate,),
                {'traversalName': traversalName})


class SingleAttributeTraverserPluginTemplate(NameTraverserPlugin):
    """Allow only a single attribute to be traversed."""

    def _traverse(self, request, name):
        return getattr(self.context, name)


def SingleAttributeTraverserPlugin(name):
    return type('SingleAttributeTraverserPlugin',
                (SingleAttributeTraverserPluginTemplate,),
                {'traversalName': name})


class AdapterTraverserPluginTemplate(NameTraverserPlugin):
    """Traverse to an adapter by name."""
    interface = None
    adapterName = ''

    def _traverse(self, request, name):
        adapter = queryAdapter(self.context, self.interface,
                               name=self.adapterName)
        if adapter is None:
            raise NotFound(self.context, name, request)

        return adapter


def AdapterTraverserPlugin(traversalName, interface, adapterName=''):
    return type('AdapterTraverserPlugin',
                (AdapterTraverserPluginTemplate,),
                {'traversalName': traversalName,
                 'adapterName': adapterName,
                 'interface': interface})


@implementer(interfaces.ITraverserPlugin)
class ContainerTraverserPlugin(object):
    """A traverser that knows how to look up objects by name in a container."""

    def __init__(self, container, request):
        self.context = container
        self.request = request

    def publishTraverse(self, request, name):
        """See zope.publisher.interfaces.IPublishTraverse"""
        subob = self.context.get(name, None)
        if subob is None:
            raise NotFound(self.context, name, request)

        return subob


@implementer(interfaces.ITraverserPlugin)
class AttributeTraverserPlugin(object):
    """A simple traverser plugin that traverses an attribute by name"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        try:
            obj = getattr(self.context, name)
        except AttributeError:
            raise NotFound(self.context, name, request)
        else:
            return obj
