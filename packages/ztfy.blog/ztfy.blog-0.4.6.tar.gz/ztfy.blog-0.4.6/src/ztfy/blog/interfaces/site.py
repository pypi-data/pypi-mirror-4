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
from zope.location.interfaces import ILocation, IPossibleSite

# import local interfaces
from ztfy.blog.interfaces import IBaseContent, IMainContent, IBaseContentRoles
from ztfy.blog.interfaces.blog import IBlogContainer
from ztfy.blog.interfaces.category import ICategoryManagerTarget
from ztfy.blog.interfaces.section import ISectionContainer
from ztfy.security.interfaces import ILocalRoleManager

# import Zope3 packages
from zope.container.constraints import contains
from zope.interface import Interface
from zope.schema import List, Object

# import local packages
from ztfy.file.schema import FileField, ImageField

from ztfy.blog import _


#
# Site management
#

class ISiteManagerInfo(IBaseContent):
    """Base site interface"""

    def getVisibleContents(request):
        """Get list of contents visible from given request"""


class ISiteManagerWriter(Interface):
    """Site writer interface"""


class ISiteManager(ISiteManagerInfo, ISiteManagerWriter, IBaseContentRoles,
                   ICategoryManagerTarget, ISectionContainer, IBlogContainer,
                   ILocation, IPossibleSite, ILocalRoleManager):
    """Site full interface"""

    contains(IMainContent)


class ISiteManagerBackInfo(Interface):
    """Site manager back-office presentation options"""

    custom_css = FileField(title=_("Custom CSS"),
                           description=_("You can provide a custom CSS for your back-office"),
                           required=False)

    custom_banner = ImageField(title=_("Custom banner"),
                               description=_("You can provide a custom image file which will be displayed on pages top"),
                               required=False)

    custom_icon = ImageField(title=_("Custom icon"),
                             description=_("You can provide a custom image file to be used as favorite icon"),
                             required=False)


class ITreeViewContents(Interface):
    """Marker interface for contents which should be displayed inside tree views"""

    values = List(title=_("Container values"),
                  value_type=Object(schema=Interface),
                  readonly=True)
