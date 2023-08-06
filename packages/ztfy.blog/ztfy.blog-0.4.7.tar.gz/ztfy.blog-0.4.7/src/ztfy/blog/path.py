### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
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

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces

# import local interfaces
from ztfy.blog.interfaces import IPathElements, IBaseContent

# import Zope3 packages
from zope.component import adapts
from zope.interface import implements
from zope.traversing.api import getPath

# import local packages


class PathElementsAdapter(object):

    implements(IPathElements)
    adapts(IBaseContent)

    def __init__(self, context):
        self.context = context

    @property
    def paths(self):
        result = []
        path = getPath(self.context)
        if not path.startswith('/'):
            return None
        elements = path.split('/')
        for index in range(len(elements)):
            result.append('/'.join(elements[0:index + 1]))
        return result[1:]
