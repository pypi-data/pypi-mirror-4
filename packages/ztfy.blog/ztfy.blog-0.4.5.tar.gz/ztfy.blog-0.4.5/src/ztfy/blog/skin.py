### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2009 Thierry Florac <tflorac AT ulthar.net>
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
from ztfy.blog.interfaces import ISkinnable

# import local interfaces

# import Zope3 packages
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from zope.traversing.api import getParent

# import local packages


class InheritedSkin(object):
    """Find content's skin locally or by inheriting via it's parents"""

    implements(ISkinnable)

    skin = FieldProperty(ISkinnable['skin'])

    def getSkin(self):
        if self.skin is not None:
            return self.skin
        parent = getParent(self)
        while parent is not None:
            adapted = ISkinnable(parent, None)
            if (adapted is not None) and (adapted.skin is not None):
                return adapted.skin
            parent = getParent(parent)
        return None
