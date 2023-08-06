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
from zope.publisher.interfaces.browser import IBrowserSkinType

# import local interfaces
from ztfy.blog.interfaces import ISkinnable

# import Zope3 packages
from zope.component import queryUtility

# import local packages
from ztfy.skin.menu import MenuItem, JsMenuItem
from ztfy.utils.traversing import getParent


class SkinTargetMenuItem(MenuItem):
    """Customized menu item specific skin targets"""

    skin = None

    def render(self):
        skinnable = getParent(self.context, ISkinnable)
        if skinnable is None:
            return u''
        skin_name = skinnable.getSkin()
        if skin_name is None:
            return u''
        skin = queryUtility(IBrowserSkinType, skin_name)
        if (skin is self.skin) or skin.extends(self.skin):
            return super(SkinTargetMenuItem, self).render()
        else:
            return u''


class SkinTargetJsMenuItem(JsMenuItem):
    """Customized JS menu item specific skin targets"""

    skin = None

    def render(self):
        skinnable = getParent(self.context, ISkinnable)
        if skinnable is None:
            return u''
        skin_name = skinnable.getSkin()
        if skin_name is None:
            return u''
        skin = queryUtility(IBrowserSkinType, skin_name)
        if (skin is self.skin) or skin.extends(self.skin):
            return super(SkinTargetJsMenuItem, self).render()
        else:
            return u''
