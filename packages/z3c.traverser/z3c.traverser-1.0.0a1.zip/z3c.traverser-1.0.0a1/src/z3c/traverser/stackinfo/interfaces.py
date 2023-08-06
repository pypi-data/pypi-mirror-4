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
"""Stackinfo interfaces
"""
from zope import interface, schema
from zope.interface.common.sequence import IExtendedReadSequence

class ITraversalStackInfo(IExtendedReadSequence):
    """A list of collected traversal stack consumers"""

class ITraversalStackConsumer(interface.Interface):
    """A traversal stack consumer"""

    __name__ = schema.TextLine(title=u'Name',
        description=u'The name under which the consumer is registered')

    arguments = schema.Tuple(title=u'Arguments',
        description=u'The argument names to be consumed')

    def consume():
        """consumes the items from the stack, and sets the __name__
        and attributes"""
