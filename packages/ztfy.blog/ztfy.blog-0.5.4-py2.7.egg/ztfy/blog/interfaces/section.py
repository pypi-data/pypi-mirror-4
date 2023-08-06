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

# import local interfaces
from ztfy.blog.interfaces import IBaseContent, IBaseContentRoles, IMainContent
from ztfy.blog.interfaces.container import IOrderedContainer
from ztfy.blog.interfaces.topic import ITopicContainer

# import Zope3 packages
from zope.container.constraints import containers, contains
from zope.interface import Interface
from zope.schema import List, Object, Bool

# import local packages
from ztfy.security.interfaces import ILocalRoleManager

from ztfy.blog import _


#
# Sections management
#

class ISectionInfo(IBaseContent):
    """Base section interface"""

    visible = Bool(title=_("Visible ?"),
                   description=_("Check to keep section visible..."),
                   default=True,
                   required=True)


class ISectionWriter(Interface):
    """Section writer interface"""


class ISection(ISectionInfo, ISectionWriter, IBaseContentRoles,
               ITopicContainer, IMainContent, ILocalRoleManager):
    """Section full interface"""

    containers('ztfy.blog.interfaces.section.ISection',
               'ztfy.blog.interfaces.site.ISiteManager')
    contains('ztfy.blog.interfaces.section.ISection',
             'ztfy.blog.interfaces.topic.ITopic')


class ISectionContainerInfo(Interface):

    sections = List(title=_("Sections list"),
                    value_type=Object(schema=ISection),
                    readonly=True)

    def getVisibleSections(request):
        """Get list of sections visible from given request"""


class ISectionContainer(ISectionContainerInfo, IOrderedContainer):
    """Section container interface"""

    contains(ISection)
