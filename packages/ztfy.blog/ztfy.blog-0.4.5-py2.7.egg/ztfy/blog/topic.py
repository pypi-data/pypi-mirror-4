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
from zope.dublincore.interfaces import IZopeDublinCore
from zope.lifecycleevent.interfaces import IObjectCreatedEvent

# import local interfaces
from hurry.workflow.interfaces import IWorkflowInfo, IWorkflowState
from ztfy.blog.interfaces.topic import ITopic

# import Zope3 packages
from zope.app.content import queryContentType
from zope.component import adapter
from zope.i18n import translate
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.blog.ordered import OrderedContainer
from ztfy.extfile.blob import BlobImage
from ztfy.i18n.property import I18nTextProperty, I18nImageProperty
from ztfy.utils.request import getRequest

from ztfy.blog import _


class Topic(OrderedContainer):

    implements(ITopic)

    title = I18nTextProperty(ITopic['title'])
    shortname = I18nTextProperty(ITopic['shortname'])
    description = I18nTextProperty(ITopic['description'])
    keywords = I18nTextProperty(ITopic['keywords'])
    heading = I18nTextProperty(ITopic['heading'])
    header = I18nImageProperty(ITopic['header'], klass=BlobImage, img_klass=BlobImage)
    illustration = I18nImageProperty(ITopic['illustration'], klass=BlobImage, img_klass=BlobImage)
    illustration_title = I18nTextProperty(ITopic['illustration_title'])
    commentable = FieldProperty(ITopic['commentable'])
    workflow_name = FieldProperty(ITopic['workflow_name'])

    @property
    def content_type(self):
        return queryContentType(self).__name__

    @property
    def paragraphs(self):
        return self.values()

    def getVisibleParagraphs(self, request=None):
        return [v for v in self.paragraphs if v.visible]

    @property
    def publication_year(self):
        return IZopeDublinCore(self).created.year

    @property
    def publication_month(self):
        return IZopeDublinCore(self).created.month


@adapter(ITopic, IObjectCreatedEvent)
def handleNewTopic(object, event):
    """Init workflow status of a new topic"""
    IWorkflowState(object).setState(None)
    IWorkflowInfo(object).fireTransition('init', translate(_("Create new topic"), context=getRequest()))
