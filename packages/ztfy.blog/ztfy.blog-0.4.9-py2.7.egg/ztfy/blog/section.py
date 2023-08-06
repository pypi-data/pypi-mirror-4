### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2009 Thierry Florac <tflorac AT ulthar.net>
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
from ztfy.blog.interfaces.section import ISection, ISectionContainer
from ztfy.blog.interfaces.site import ITreeViewContents
from ztfy.blog.interfaces.topic import ITopic

# import Zope3 packages
from zope.app.content import queryContentType
from zope.component import adapts
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.blog.ordered import OrderedContainer
from ztfy.blog.skin import InheritedSkin
from ztfy.extfile.blob import BlobImage
from ztfy.i18n.property import I18nTextProperty, I18nImageProperty
from ztfy.security.property import RolePrincipalsProperty
from ztfy.utils.security import unproxied
from ztfy.utils.unicode import translateString
from ztfy.workflow.interfaces import IWorkflowContent


class Section(OrderedContainer, InheritedSkin):

    implements(ISection, ISectionContainer)

    __roles__ = ('ztfy.BlogManager', 'ztfy.BlogContributor')

    title = I18nTextProperty(ISection['title'])
    shortname = I18nTextProperty(ISection['shortname'])
    description = I18nTextProperty(ISection['description'])
    keywords = I18nTextProperty(ISection['keywords'])
    heading = I18nTextProperty(ISection['heading'])
    header = I18nImageProperty(ISection['header'], klass=BlobImage, img_klass=BlobImage)
    illustration = I18nImageProperty(ISection['illustration'], klass=BlobImage, img_klass=BlobImage)
    illustration_title = I18nTextProperty(ISection['illustration_title'])
    visible = FieldProperty(ISection['visible'])

    administrators = RolePrincipalsProperty(ISection['administrators'], role='ztfy.BlogManager')
    contributors = RolePrincipalsProperty(ISection['contributors'], role='ztfy.BlogContributor')

    @property
    def content_type(self):
        return queryContentType(self).__name__

    @property
    def sections(self):
        """See `ISectionContainer` interface"""
        return [v for v in self.values() if ISection.providedBy(v)]

    def getVisibleSections(self):
        """See `ISectionContainer` interface"""
        return [v for v in self.sections if v.visible]

    @property
    def topics(self):
        """See `ITopicContainer` interface"""
        return [v for v in self.values() if ITopic.providedBy(v)]

    def getVisibleTopics(self):
        """See `ITopicContainer` interface"""
        return [t for t in self.topics if IWorkflowContent(t).isVisible()]

    def addTopic(self, topic):
        """See `ITopicContainer` interface"""
        language = II18n(self).getDefaultLanguage()
        title = translateString(topic.shortname.get(language), forceLower=True, spaces='-')
        if len(title) > 40:
            title = title[:40]
            title = title[:title.rfind('-')]
        self[title + '.html'] = unproxied(topic)


class SectionTreeViewContentsAdapter(object):

    adapts(ISection)
    implements(ITreeViewContents)

    def __init__(self, context):
        self.context = context

    @property
    def values(self):
        return self.context.values()
