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
from hurry.query.interfaces import IQuery
from z3c.language.switch.interfaces import II18n
from zope.intid.interfaces import IIntIds

# import local interfaces
from ztfy.blog.interfaces import IBaseContent
from ztfy.blog.interfaces.container import IOrderedContainer
from ztfy.skin.interfaces import IDefaultView, IContainedDefaultView
from ztfy.skin.layer import IZTFYBrowserLayer, IZTFYBackLayer

# import Zope3 packages
from z3c.jsonrpc.publisher import MethodPublisher
from zope.component import adapts, getUtility
from zope.interface import implements, Interface
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.utils.catalog.index import Text


class BaseContentDefaultViewAdapter(object):
    """Default front-office URL adapter"""

    adapts(IBaseContent, IZTFYBrowserLayer, Interface)
    implements(IDefaultView)

    viewname = ''

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    def getAbsoluteURL(self):
        return absoluteURL(self.context, self.request)


class BaseContentDefaultBackViewAdapter(object):
    """Default back-office URL adapter"""

    adapts(IBaseContent, IZTFYBackLayer, Interface)
    implements(IDefaultView)

    viewname = '@@properties.html'

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    def getAbsoluteURL(self):
        return '%s/%s' % (absoluteURL(self.context, self.request), self.viewname)


class BaseContainedDefaultBackViewAdapter(object):
    """Default container back-office URL adapter"""

    adapts(IOrderedContainer, IZTFYBackLayer, Interface)
    implements(IContainedDefaultView)

    viewname = '@@contents.html'

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    def getAbsoluteURL(self):
        return '%s/%s' % (absoluteURL(self.context, self.request), self.viewname)


class BaseContentSearchView(MethodPublisher):
    """Base content XML-RPC search view"""

    def search(self, query):
        if not query:
            return []
        query_util = getUtility(IQuery)
        intids = getUtility(IIntIds)
        result = []
        for obj in query_util.searchResults(Text(('Catalog', 'title'),
                                                 { 'query': query + '*',
                                                   'ranking': True })):
            result.append({ 'value': str(intids.register(obj)),
                            'caption': II18n(obj).queryAttribute('title') })
        return result
