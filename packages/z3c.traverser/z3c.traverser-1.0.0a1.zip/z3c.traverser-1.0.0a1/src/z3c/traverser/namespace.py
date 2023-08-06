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
"""++principal++ Namespace
"""
from zope.traversing.namespace import view
from zope.publisher.interfaces import Unauthorized

class principal(view):
    """a principal namespace"""

    def traverse(self, name, ignored):
        self.request.shiftNameToApplication()
        pid = self.request.principal.id
        if name != pid:
            raise Unauthorized("++principal++%s" % name)
        return self.context
