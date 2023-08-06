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
from ztfy.blog.defaultskin.interfaces import IContainerSitemapInfo

# import Zope3 packages

# import local packages
from ztfy.skin.page import BaseTemplateBasedPage


class SiteManagerMapsIndexView(BaseTemplateBasedPage):
    """Site manager sitemaps index view"""


def getValues(parent, context, output):
    output.append(context)
    contents = IContainerSitemapInfo(context, None)
    if contents is not None:
        for item in contents.values:
            getValues(context, item, output)


class SiteManagerSitemapView(BaseTemplateBasedPage):
    """Site manager sitemap view"""

    def getContents(self):
        result = []
        getValues(None, self.context, result)
        return result
