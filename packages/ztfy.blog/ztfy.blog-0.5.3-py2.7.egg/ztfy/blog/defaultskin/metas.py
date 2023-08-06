### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2011 Thierry Florac <tflorac AT ulthar.net>
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
from z3c.language.switch.interfaces import II18n

# import local interfaces
from ztfy.blog.defaultskin.interfaces import IHTTPEquivMetaHeader, IContentMetaHeader, IPropertyMetaHeader, \
                                             ILinkMetaHeader, IContentMetasHeaders, IPageMetasHeaders
from ztfy.blog.interfaces import IBaseContent

# import Zope3 packages
from zope.component import adapts, getAdapters
from zope.interface import implements, Interface

# import local packages


class ContentMeta(object):
    """Base content meta header"""

    implements(IContentMetaHeader)

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def render(self):
        return """<meta name="%(name)s" content="%(content)s" />""" % { 'name': self.name,
                                                                        'content': self.value }


class HTTPEquivMeta(object):
    """HTTP-Equiv meta header, mainly used for content-type"""

    implements(IHTTPEquivMetaHeader)

    def __init__(self, http_equiv, value):
        self.http_equiv = http_equiv
        self.value = value

    def render(self):
        return """<meta http-equiv="%(http_equiv)s" content="%(content)s" />""" % { 'http_equiv': self.http_equiv,
                                                                                    'content': self.value }


class PropertyMeta(object):
    """Property meta header, mainly used for Facebook app_id"""

    implements(IPropertyMetaHeader)

    def __init__(self, property, value):
        self.property = property
        self.value = value

    def render(self):
        return """<meta property="%(property)s" content="%(content)s" />""" % { 'property': self.property,
                                                                                'content': self.value }


class LinkMeta(object):
    """Link meta header, mainly used for CSS or RSS links"""

    implements(ILinkMetaHeader)

    def __init__(self, rel, type, href):
        self.rel = rel
        self.type = type
        self.href = href

    def render(self):
        return """<link rel="%(rel)s" type="%(type)s" href="%(href)s" />""" % { 'rel': self.rel,
                                                                                'type': self.type,
                                                                                'href': self.href }


class ContentMetasAdapter(object):
    """Generic content metas adapter"""

    adapts(Interface, Interface)
    implements(IPageMetasHeaders)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def metas(self):
        """Extract headers from all available metas adapters"""
        result = []
        for _name, adapter in getAdapters((self.context, self.request), IContentMetasHeaders):
            result.extend(adapter.metas)
        return result


class BaseContentMetasHeadersAdapter(object):
    """Base content metas adapter"""

    adapts(IBaseContent, Interface)
    implements(IContentMetasHeaders)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def metas(self):
        result = []
        result.append(HTTPEquivMeta('Content-Type', 'text/html; charset=UTF-8'))
        i18n = II18n(self.context, None)
        if i18n is None:
            return result
        description = i18n.queryAttribute('description', request=self.request)
        if description:
            result.append(ContentMeta('description', description.replace('\n', ' ')))
        keywords = i18n.queryAttribute('keywords', request=self.request)
        if keywords:
            result.append(ContentMeta('keywords', keywords))
        return result
