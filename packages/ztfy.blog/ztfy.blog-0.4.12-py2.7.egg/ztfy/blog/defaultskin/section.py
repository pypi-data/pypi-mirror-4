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
from ztfy.blog.browser.interfaces.skin import ISectionIndexView, IPresentationTarget
from ztfy.blog.defaultskin.interfaces import ISectionPresentationInfo, IContainerSitemapInfo, SECTION_DISPLAY_FIRST
from ztfy.blog.defaultskin.layer import IZBlogDefaultLayer
from ztfy.blog.interfaces.section import ISection

# import Zope3 packages
from z3c.template.template import getViewTemplate
from zope.component import adapter, adapts
from zope.container.contained import Contained
from zope.interface import implementer, implements
from zope.publisher.browser import BrowserView
from zope.schema.fieldproperty import FieldProperty
from zope.traversing.api import getParents
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.blog.browser.section import BaseSectionIndexView
from ztfy.blog.defaultskin.menu import DefaultSkinJsMenuItem

from ztfy.blog import _


SECTION_PRESENTATION_KEY = 'ztfy.blog.defaultskin.section.presentation'


class SectionPresentationViewMenuItem(DefaultSkinJsMenuItem):
    """Section presentation menu item"""

    title = _(" :: Presentation model...")


class SectionPresentation(Persistent, Contained):
    """Section presentation infos"""

    implements(ISectionPresentationInfo)

    header_format = FieldProperty(ISectionPresentationInfo['header_format'])
    header_position = FieldProperty(ISectionPresentationInfo['header_position'])
    display_googleplus = FieldProperty(ISectionPresentationInfo['display_googleplus'])
    display_fb_like = FieldProperty(ISectionPresentationInfo['display_fb_like'])
    presentation_mode = FieldProperty(ISectionPresentationInfo['presentation_mode'])


@adapter(ISection)
@implementer(ISectionPresentationInfo)
def SectionPresentationFactory(context):
    annotations = IAnnotations(context)
    presentation = annotations.get(SECTION_PRESENTATION_KEY)
    if presentation is None:
        presentation = annotations[SECTION_PRESENTATION_KEY] = SectionPresentation()
    return presentation


class SectionPresentationTargetAdapter(object):

    adapts(ISection, IZBlogDefaultLayer)
    implements(IPresentationTarget)

    target_interface = ISectionPresentationInfo

    def __init__(self, context, request):
        self.context, self.request = context, request


class SectionIndexView(BaseSectionIndexView):
    """Section index page"""

    implements(ISectionIndexView)

    def render(self):
        if self.topics and (self.presentation.presentation_mode == SECTION_DISPLAY_FIRST):
            topic = self.topics[0]
            self.request.response.redirect(absoluteURL(topic, self.request))
            return u''
        return super(SectionIndexView, self).render()


class SectionSectionsView(BrowserView):
    """Section sub-sections view"""

    __call__ = getViewTemplate()

    @property
    def sections(self):
        result = []
        context = None
        parents = getParents(self.context) + [self.context, ]
        sections = [s for s in getParents(self.context) if ISection.providedBy(s)]
        if sections:
            context = sections[-1]
        elif ISection.providedBy(self.context):
            context = self.context
        if context is not None:
            for section in (s for s in context.sections if s.visible):
                selected = section in parents
                subsections = ()
                if selected and ISection.providedBy(section):
                    subsections = [s for s in section.sections if s.visible]
                result.append({ 'section': section,
                                'selected': selected,
                                'subsections': subsections,
                                'subselected': set(subsections) & set(parents) })
        return result


class SectionSitemapAdapter(object):
    """Section sitemap adapter"""

    adapts(ISection)
    implements(IContainerSitemapInfo)

    def __init__(self, context):
        self.context = context

    @property
    def values(self):
        return self.context.getVisibleSections() + self.context.getVisibleTopics()
