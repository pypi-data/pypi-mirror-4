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

# import Zope3 packages

# import local packages
from ztfy.blog.browser.menu import SkinTargetMenuItem, SkinTargetJsMenuItem
from ztfy.blog.defaultskin.layer import IZBlogDefaultSkin



class DefaultSkinMenuItem(SkinTargetMenuItem):
    """Customized menu item for ZBlog skin targets"""

    skin = IZBlogDefaultSkin


class DefaultSkinJsMenuItem(SkinTargetJsMenuItem):
    """Customized JS menu item for ZBlog skin targets"""

    skin = IZBlogDefaultSkin
