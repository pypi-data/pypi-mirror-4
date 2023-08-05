### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2012 Thierry Florac <tflorac AT ulthar.net>
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
from ztfy.blog.defaultskin.layer import IZBlogDefaultLayer

# import Zope3 packages
from zope.component import adapts
from zope.interface import Interface

# import local packages
from ztfy.skin.viewlet import ContentProviderBase


class GooglePlusOneContentProvider(ContentProviderBase):
    """Google +1 viewlet javascript code"""

    adapts(Interface, IZBlogDefaultLayer, Interface)

    def update(self):
        self.presentation = getattr(self.__parent__, 'presentation', None)

    def render(self):
        if not getattr(self.presentation, 'display_googleplus', False):
            return ''
        return super(GooglePlusOneContentProvider, self).render()
