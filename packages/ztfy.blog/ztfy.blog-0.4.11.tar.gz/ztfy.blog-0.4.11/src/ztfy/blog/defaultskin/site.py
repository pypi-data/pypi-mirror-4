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
from persistent import Persistent

# import Zope3 interfaces
from zope.annotation.interfaces import IAnnotations

# import local interfaces
from ztfy.blog.browser.interfaces.skin import IPresentationTarget
from ztfy.blog.defaultskin.interfaces import ISiteManagerPresentationInfo, IContainerSitemapInfo, \
                                             IContentMetasHeaders
from ztfy.blog.defaultskin.layer import IZBlogDefaultLayer
from ztfy.blog.interfaces.site import ISiteManager

# import Zope3 packages
from zope.component import adapter, adapts, queryMultiAdapter
from zope.container.contained import Contained
from zope.interface import implementer, implements
from zope.location import locate
from zope.schema.fieldproperty import FieldProperty
from zope.traversing.browser.absoluteurl import absoluteURL

# import local packages
from ztfy.blog.defaultskin.menu import DefaultSkinJsMenuItem
from ztfy.blog.defaultskin.metas import LinkMeta
from ztfy.blog.browser.site import BaseSiteManagerIndexView
from ztfy.i18n.property import I18nTextProperty
from ztfy.jqueryui import jquery_multiselect, jquery_jsonrpc
from ztfy.skin.page import BaseTemplateBasedPage
from ztfy.workflow.interfaces import IWorkflowContent

from ztfy.blog import _


SITE_MANAGER_PRESENTATION_KEY = 'ztfy.blog.defaultskin.presentation'


class SiteManagerPresentationViewMenuItem(DefaultSkinJsMenuItem):
    """Site manager presentation menu item"""

    title = _(" :: Presentation model...")

    def render(self):
        jquery_jsonrpc.need()
        jquery_multiselect.need()
        return super(SiteManagerPresentationViewMenuItem, self).render()


class SiteManagerPresentation(Persistent, Contained):
    """Site manager presentation infos"""

    implements(ISiteManagerPresentationInfo)

    header_format = FieldProperty(ISiteManagerPresentationInfo['header_format'])
    header_position = FieldProperty(ISiteManagerPresentationInfo['header_position'])
    display_googleplus = FieldProperty(ISiteManagerPresentationInfo['display_googleplus'])
    main_blogs = FieldProperty(ISiteManagerPresentationInfo['main_blogs'])
    nb_entries = FieldProperty(ISiteManagerPresentationInfo['nb_entries'])
    owner = FieldProperty(ISiteManagerPresentationInfo['owner'])
    owner_mailto = FieldProperty(ISiteManagerPresentationInfo['owner_mailto'])
    signature = I18nTextProperty(ISiteManagerPresentationInfo['signature'])
    facebook_app_id = FieldProperty(ISiteManagerPresentationInfo['facebook_app_id'])
    disqus_site_id = FieldProperty(ISiteManagerPresentationInfo['disqus_site_id'])


@adapter(ISiteManager)
@implementer(ISiteManagerPresentationInfo)
def SiteManagerPresentationFactory(context):
    annotations = IAnnotations(context)
    presentation = annotations.get(SITE_MANAGER_PRESENTATION_KEY)
    if presentation is None:
        presentation = annotations[SITE_MANAGER_PRESENTATION_KEY] = SiteManagerPresentation()
        locate(presentation, context, '++presentation++')
    return presentation


class SiteManagerPresentationTargetAdapter(object):

    adapts(ISiteManager, IZBlogDefaultLayer)
    implements(IPresentationTarget)

    target_interface = ISiteManagerPresentationInfo

    def __init__(self, context, request):
        self.context, self.request = context, request


class SiteManagerIndexView(BaseSiteManagerIndexView):
    """Site manager index page"""

    @property
    def topics(self):
        blogs = self.presentation.main_blogs
        if not blogs:
            return []
        topics = []
        [topics.extend(blog.getVisibleTopics()) for blog in blogs if blog.visible]
        topics.sort(key=lambda x: IWorkflowContent(x).publication_effective_date, reverse=True)
        return topics[:self.presentation.nb_entries]


class SiteManagerRssLinkAdapter(object):

    adapts(ISiteManager, IZBlogDefaultLayer)
    implements(IContentMetasHeaders)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def metas(self):
        return [ LinkMeta('alternate', 'application/rss+xml', '%s/@@rss.xml' % absoluteURL(self.context, self.request)) ]


class SiteManagerRssView(BaseTemplateBasedPage):
    """Site manager RSS view"""

    def update(self):
        adapter = queryMultiAdapter((self.context, self.request, self), IPresentationTarget)
        if adapter is None:
            adapter = queryMultiAdapter((self.context, self.request), IPresentationTarget)
        if adapter is not None:
            interface = adapter.target_interface
            self.presentation = interface(self.context)

    @property
    def topics(self):
        blogs = self.presentation.main_blogs
        if not blogs:
            return []
        topics = []
        [topics.extend(blog.getVisibleTopics()) for blog in blogs if blog.visible]
        topics.sort(key=lambda x: IWorkflowContent(x).publication_effective_date, reverse=True)
        return topics[:self.presentation.nb_entries]


class SiteManagerSitemapAdapter(object):
    """Site manager sitemap adapter"""

    adapts(ISiteManager)
    implements(IContainerSitemapInfo)

    def __init__(self, context):
        self.context = context

    @property
    def values(self):
        return [v for v in self.context.values() if getattr(v, 'visible', False)]
