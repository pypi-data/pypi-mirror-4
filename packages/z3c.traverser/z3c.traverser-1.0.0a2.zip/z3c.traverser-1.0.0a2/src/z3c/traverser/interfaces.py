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
"""Pluggable Traverser Interfaces

This implementation is independent of the presentation type. Sub-interfaces
must be written for every specific presentation type.
"""
from zope.publisher.interfaces import IPublishTraverse


class IPluggableTraverser(IPublishTraverse):
    """A pluggable traverser.

    This traverser traverses a name by utilizing helper traversers that are
    registered as ``ITraverserPlugin`` subscribers.
    """


class ITraverserPlugin(IPublishTraverse):
    """A plugin for the pluggable traverser."""
