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
from ztfy.blog.browser.interfaces.skin import IPresentationTarget

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces

# import local interfaces
from ztfy.blog.defaultskin.interfaces import IContentMetasHeaders
from ztfy.blog.interfaces.google import IGoogleAnalytics
from ztfy.blog.interfaces.site import ISiteManager

# import Zope3 packages
from zope.component import adapts, queryMultiAdapter
from zope.interface import implements, Interface

# import local packages
from ztfy.blog.defaultskin.metas import ContentMeta, PropertyMeta
from ztfy.utils.traversing import getParent


class GoogleMetasSiteManagerAdapter(object):
    """Google site verification meta header adapter"""

    adapts(ISiteManager, Interface)
    implements(IContentMetasHeaders)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def metas(self):
        result = []
        google = IGoogleAnalytics(self.context, None)
        if google is not None:
            code = google.verification_code
            if code:
                result.append(ContentMeta('google-site-verification', code))
        return result


class FacebookMetasAdapter(object):
    """Facebook meta header adapter"""

    adapts(Interface, Interface)
    implements(IContentMetasHeaders)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def metas(self):
        result = []
        manager = getParent(self.context, ISiteManager)
        if manager is not None:
            adapter = queryMultiAdapter((manager, self.request), IPresentationTarget)
            if adapter is not None:
                interface = adapter.target_interface
                presentation = interface(manager)
                app_id = getattr(presentation, 'facebook_app_id', None)
                if app_id:
                    result.append(PropertyMeta('fb:app_id', app_id))
        return result
