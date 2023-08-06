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
from ztfy.skin.interfaces import IContainerAddFormMenuTarget

# import Zope3 packages
from zope.interface import Interface, Attribute

# import local packages

from ztfy.blog import _


class ISiteManagerTreeView(Interface):
    """Marker interface for site manager tree view"""


class ISiteManagerTreeViewContent(Interface):
    """Interface for site manager tree view contents"""

    resourceLibrary = Attribute(_("Resource library"))

    cssClass = Attribute(_("CSS class"))


class IMainContentAddFormMenuTarget(IContainerAddFormMenuTarget):
    """Marker interface for main content add form menu item"""


class IBlogAddFormMenuTarget(IMainContentAddFormMenuTarget):
    """Marker interface for blog add menu item"""


class ISectionAddFormMenuTarget(IMainContentAddFormMenuTarget):
    """Marker interface for section add form menu"""


class ITopicAddFormMenuTarget(IMainContentAddFormMenuTarget):
    """Marker interface for topic add menu item"""


class ITopicElementAddFormMenuTarget(IContainerAddFormMenuTarget):
    """Marker interface for topic element add menu item"""
