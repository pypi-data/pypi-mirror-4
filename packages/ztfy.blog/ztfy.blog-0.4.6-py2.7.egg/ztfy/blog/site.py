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
from BTrees.OOBTree import OOBTree
from persistent import Persistent
from persistent.list import PersistentList

# import Zope3 interfaces
from zope.annotation.interfaces import IAnnotations

# import local interfaces
from ztfy.blog.interfaces.blog import IBlog
from ztfy.blog.interfaces.section import ISection
from ztfy.blog.interfaces.site import ISiteManager, ISiteManagerBackInfo, ITreeViewContents

# import Zope3 packages
from zope.app.content import queryContentType
from zope.component import adapter, adapts
from zope.event import notify
from zope.interface import implementer, implements
from zope.location.location import Location, locate
from zope.site import SiteManagerContainer

# import local packages
from ztfy.blog.ordered import OrderedContainer
from ztfy.blog.skin import InheritedSkin
from ztfy.extfile.blob import BlobFile, BlobImage
from ztfy.file.property import ImageProperty, FileProperty
from ztfy.i18n.property import I18nTextProperty, I18nImageProperty
from ztfy.security.property import RolePrincipalsProperty
from ztfy.utils.site import NewSiteManagerEvent


class SiteManager(OrderedContainer, SiteManagerContainer, InheritedSkin):
    """Main site manager class"""

    implements(ISiteManager)

    __roles__ = ('ztfy.BlogManager', 'ztfy.BlogContributor')

    title = I18nTextProperty(ISiteManager['title'])
    shortname = I18nTextProperty(ISiteManager['shortname'])
    description = I18nTextProperty(ISiteManager['description'])
    keywords = I18nTextProperty(ISiteManager['keywords'])
    heading = I18nTextProperty(ISiteManager['heading'])
    header = I18nImageProperty(ISiteManager['header'], klass=BlobImage, img_klass=BlobImage)
    illustration = I18nImageProperty(ISiteManager['illustration'], klass=BlobImage, img_klass=BlobImage)
    illustration_title = I18nTextProperty(ISiteManager['illustration_title'])

    administrators = RolePrincipalsProperty(ISiteManager['administrators'], role='ztfy.BlogManager')
    contributors = RolePrincipalsProperty(ISiteManager['contributors'], role='ztfy.BlogContributor')

    def __init__(self, *args, **kw):
        self._data = OOBTree()
        self._order = PersistentList()

    @property
    def content_type(self):
        return queryContentType(self).__name__

    def setSiteManager(self, sm):
        SiteManagerContainer.setSiteManager(self, sm)
        notify(NewSiteManagerEvent(self))

    def getVisibleContents(self):
        return [v for v in self.values() if getattr(v, 'visible', True)]

    def getVisibleSections(self):
        """See `ISectionContainer` interface"""
        return [v for v in self.getVisibleContents() if ISection.providedBy(v)]

    @property
    def blogs(self):
        return [v for v in self.values() if IBlog.providedBy(v)]


class SiteManagerBackInfo(Persistent, Location):
    """Main site back-office presentation options"""

    implements(ISiteManagerBackInfo)

    custom_css = FileProperty(ISiteManagerBackInfo['custom_css'], klass=BlobFile)
    custom_banner = ImageProperty(ISiteManagerBackInfo['custom_banner'], klass=BlobImage, img_klass=BlobImage)
    custom_icon = ImageProperty(ISiteManagerBackInfo['custom_icon'])


SITE_MANAGER_BACK_INFO_KEY = 'ztfy.blog.backoffice.presentation'

@adapter(ISiteManager)
@implementer(ISiteManagerBackInfo)
def SiteManagerBackInfoFactory(context):
    annotations = IAnnotations(context)
    info = annotations.get(SITE_MANAGER_BACK_INFO_KEY)
    if info is None:
        info = annotations[SITE_MANAGER_BACK_INFO_KEY] = SiteManagerBackInfo()
        locate(info, context, '++back++')
    return info


class SiteManagerTreeViewContentsAdapter(object):

    adapts(ISiteManager)
    implements(ITreeViewContents)

    def __init__(self, context):
        self.context = context

    @property
    def values(self):
        return self.context.values()
