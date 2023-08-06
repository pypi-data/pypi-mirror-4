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
import pytz
from datetime import datetime

# import Zope3 interfaces
from z3c.language.negotiator.interfaces import INegotiatorManager
from z3c.language.switch.interfaces import II18n
from zope.dublincore.interfaces import IZopeDublinCore
from zope.schema.interfaces import IVocabularyFactory

# import local interfaces
from hurry.query.interfaces import IQuery
from ztfy.blog.interfaces.blog import IBlog, IBlogFolder, IBlogContainer
from ztfy.blog.interfaces.topic import ITopic

# import Zope3 packages
from zope.app.content import queryContentType
from zope.component import getUtility, queryUtility
from zope.site.folder import Folder
from zope.event import notify
from zope.interface import implements, classProvides
from zope.schema.fieldproperty import FieldProperty
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.security.proxy import removeSecurityProxy
from zope.traversing.api import getName, getPath

# import local packages
from hurry.query.set import AnyOf
from ztfy.blog.skin import InheritedSkin
from ztfy.extfile.blob import BlobImage
from ztfy.i18n.property import I18nTextProperty, I18nImageProperty
from ztfy.security.property import RolePrincipalsProperty
from ztfy.utils.security import unproxied
from ztfy.utils.site import NewSiteManagerEvent
from ztfy.utils.traversing import getParent
from ztfy.utils.unicode import translateString
from ztfy.workflow.interfaces import IWorkflowContent


class BlogFolder(Folder):
    """Custom class used to store topics"""

    implements(IBlogFolder)

    @property
    def topics(self):
        return [v for v in self.values() if ITopic.providedBy(v)]


class Blog(Folder, InheritedSkin):

    implements(IBlog)

    __roles__ = ('zope.Manager', 'ztfy.BlogManager', 'ztfy.BlogContributor', 'ztfy.BlogOperator')

    title = I18nTextProperty(IBlog['title'])
    shortname = I18nTextProperty(IBlog['shortname'])
    description = I18nTextProperty(IBlog['description'])
    keywords = I18nTextProperty(IBlog['keywords'])
    heading = I18nTextProperty(IBlog['heading'])
    header = I18nImageProperty(IBlog['header'], klass=BlobImage, img_klass=BlobImage)
    illustration = I18nImageProperty(IBlog['illustration'], klass=BlobImage, img_klass=BlobImage)
    illustration_title = I18nTextProperty(IBlog['illustration_title'])
    visible = FieldProperty(IBlog['visible'])

    administrators = RolePrincipalsProperty(IBlog['administrators'], role='ztfy.BlogManager')
    contributors = RolePrincipalsProperty(IBlog['contributors'], role='ztfy.BlogContributor')

    @property
    def content_type(self):
        return queryContentType(self).__name__

    def setSiteManager(self, sm):
        Folder.setSiteManager(self, sm)
        notify(NewSiteManagerEvent(self))

    @property
    def topics(self):
        """See `ITopicContainer` interface"""
        query = getUtility(IQuery)
        items = query.searchResults(AnyOf(('Catalog', 'paths'), (getPath(self),)))
        return sorted([item for item in items if ITopic.providedBy(item)],
                      key=lambda x: IZopeDublinCore(x).modified,
                      reverse=True)

    def getVisibleTopics(self):
        """See `ITopicContainer` interface"""
        return sorted([t for t in self.topics if IWorkflowContent(t).isVisible()],
                      key=lambda x: IWorkflowContent(x).publication_effective_date,
                      reverse=True)

    def addTopic(self, topic):
        """See `ITopicContainer` interface"""
        # initialize sub-folders
        now = datetime.now(pytz.UTC)
        year, month = str(now.year), '%02d' % now.month
        y_folder = self.get(year)
        if y_folder is None:
            self[year] = y_folder = BlogFolder()
        m_folder = y_folder.get(month)
        if m_folder is None:
            y_folder[month] = m_folder = BlogFolder()
        # lookup server language
        manager = queryUtility(INegotiatorManager)
        if manager is not None:
            lang = INegotiatorManager(manager).serverLanguage
        else:
            lang = 'en'
        # get topic name
        title = translateString(topic.shortname.get(lang), forceLower=True, spaces='-')
        if len(title) > 40:
            title = title[:40]
            title = title[:title.rfind('-')]
        index = 0
        base_title = title + '.html'
        while base_title in m_folder:
            index += 1
            base_title = '%s-%02d.html' % (title, index)
        m_folder[base_title] = unproxied(topic)


class BlogsVocabulary(SimpleVocabulary):

    classProvides(IVocabularyFactory)

    def __init__(self, context):
        container = getParent(context, IBlogContainer)
        terms = [SimpleTerm(removeSecurityProxy(b), getName(b), II18n(b).queryAttribute('title')) for b in container.blogs]
        super(BlogsVocabulary, self).__init__(terms)
