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
from zope.dublincore.interfaces import IZopeDublinCore

# import local interfaces
from ztfy.blog.browser.interfaces.skin import IPresentationTarget
from ztfy.blog.defaultskin.interfaces import ISiteManagerPresentationInfo, IBlogPresentationInfo, \
                                             ITopicPresentationInfo
from ztfy.blog.defaultskin.layer import IZBlogDefaultLayer
from ztfy.blog.interfaces import IUniqueID
from ztfy.blog.interfaces.blog import IBlog
from ztfy.blog.interfaces.category import ICategorizedContent
from ztfy.blog.interfaces.link import ILinkContainer
from ztfy.blog.interfaces.topic import ITopic
from ztfy.blog.interfaces.site import ISiteManager

# import Zope3 packages
from z3c.template.template import getViewTemplate
from zope.component import adapter, adapts, queryMultiAdapter
from zope.container.contained import Contained
from zope.interface import implementer, implements
from zope.publisher.browser import BrowserView
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.blog.browser.topic import BaseTopicIndexView
from ztfy.blog.defaultskin.menu import DefaultSkinJsMenuItem
from ztfy.security.search import getPrincipal
from ztfy.utils.traversing import getParent
from ztfy.workflow.interfaces import IWorkflowContent

from ztfy.blog import _


TOPIC_PRESENTATION_KEY = 'ztfy.blog.defaultskin.topic.presentation'


class TopicPresentationViewMenuItem(DefaultSkinJsMenuItem):
    """Site manager presentation menu item"""

    title = _(" :: Presentation model...")


class TopicPresentation(Persistent, Contained):
    """Site manager presentation infos"""

    implements(ITopicPresentationInfo)

    header_format = FieldProperty(ITopicPresentationInfo['header_format'])
    header_position = FieldProperty(ITopicPresentationInfo['header_position'])
    display_googleplus = FieldProperty(ITopicPresentationInfo['display_googleplus'])
    display_fb_like = FieldProperty(ITopicPresentationInfo['display_fb_like'])
    illustration_position = FieldProperty(ITopicPresentationInfo['illustration_position'])
    linked_resources = FieldProperty(ITopicPresentationInfo['linked_resources'])


@adapter(ITopic)
@implementer(ITopicPresentationInfo)
def TopicPresentationFactory(context):
    annotations = IAnnotations(context)
    presentation = annotations.get(TOPIC_PRESENTATION_KEY)
    if presentation is None:
        presentation = annotations[TOPIC_PRESENTATION_KEY] = TopicPresentation()
    return presentation


class TopicPresentationTargetAdapter(object):

    adapts(ITopic, IZBlogDefaultLayer)
    implements(IPresentationTarget)

    target_interface = ITopicPresentationInfo

    def __init__(self, context, request):
        self.context, self.request = context, request


class TopicIndexList(BrowserView):
    """Topic list item"""

    __call__ = getViewTemplate()

    @property
    def presentation(self):
        return ITopicPresentationInfo(self.context)


class TopicIndexPreview(TopicIndexList):
    """Topic index preview"""

    __call__ = getViewTemplate()

    @property
    def author(self):
        return getPrincipal(IZopeDublinCore(self.context).creators[0])

    @property
    def date(self):
        return IWorkflowContent(self.context).publication_effective_date


class TopicIndexView(BaseTopicIndexView):
    """Topic index page"""

    @property
    def author(self):
        return getPrincipal(IZopeDublinCore(self.context).creators[0])

    @property
    def date(self):
        return IWorkflowContent(self.context).publication_effective_date


class TopicResourcesView(BrowserView):
    """Topic resources view"""

    __call__ = getViewTemplate()

    @property
    def resources(self):
        adapter = queryMultiAdapter((self.context, self.request), IPresentationTarget)
        if adapter is not None:
            interface = adapter.target_interface
        else:
            interface = ITopicPresentationInfo
        adapter = queryMultiAdapter((self.context, self.request), interface)
        if adapter is None:
            adapter = interface(self.context)
        return adapter.linked_resources


class TopicLinksView(BrowserView):
    """Topic links view"""

    __call__ = getViewTemplate()

    @property
    def links(self):
        return ILinkContainer(self.context).getVisibleLinks()


class TopicTagsView(BrowserView):
    """Topic tags view"""

    __call__ = getViewTemplate()

    @property
    def tags(self):
        return ICategorizedContent(self.context).categories


class TopicCommentsView(BrowserView):
    """Topic comments view"""

    __call__ = getViewTemplate()

    @property
    def oid(self):
        return IUniqueID(self.context).oid

    @property
    def presentation(self):
        if not self.context.commentable:
            return None
        site = getParent(self.context, ISiteManager)
        if site is not None:
            return ISiteManagerPresentationInfo(site)
        blog = getParent(self.context, IBlog)
        if blog is not None:
            return IBlogPresentationInfo(blog)
        return None
