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
from ztfy.skin.interfaces import IDefaultView
from ztfy.skin.layer import IZTFYBrowserLayer

# import Zope3 packages
from zope.component import queryMultiAdapter
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.skin.menu import MenuItem

from ztfy.blog import _


class BackToFrontMenu(MenuItem):

    title = _("Back to front-office")

    @property
    def url(self):
        result = self.viewURL
        if not result:
            result = absoluteURL(self.context, self.request)
        elif not result.startswith('/'):
            result = '%s/%s' % (absoluteURL(self.context, self.request), result)
        return result.replace('/++skin++ZMI', '')

    @property
    def viewURL(self):
        adapter = queryMultiAdapter((self.context, IZTFYBrowserLayer, self.__parent__), IDefaultView)
        if adapter is not None:
            return adapter.viewname
        return ''
