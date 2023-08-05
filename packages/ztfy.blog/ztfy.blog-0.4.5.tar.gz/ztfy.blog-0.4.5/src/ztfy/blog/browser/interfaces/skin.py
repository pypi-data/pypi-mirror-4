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

# import Zope3 packages
from zope.interface import Interface, Attribute

# import local packages

from ztfy.blog import _


# Presentation management interfaces

class IBasePresentationInfo(Interface):
    """Base interface for presentation infos"""


class IPresentationForm(Interface):
    """Marker interface for default presentation edit form"""


class IPresentationTarget(Interface):
    """Interface used inside skin-related edit forms"""

    target_interface = Attribute(_("Presentation form target interface"))


# Base front-office views

class IBaseViewlet(Interface):
    """Marker interface for base viewlets"""


class IBaseIndexView(Interface):
    """Marker interface for base index view"""


class ISiteManagerIndexView(IBaseIndexView):
    """Site manager index view marker interface"""


class IBlogIndexView(IBaseIndexView):
    """Blog index view marker interface"""


class IBlogFolderIndexView(IBaseIndexView):
    """Blog folder index view marker interface"""


class ISectionIndexView(IBaseIndexView):
    """Section index view marker interface"""


class ITopicIndexView(Interface):
    """Topic index view marker interface"""


class ICategoryIndexView(Interface):
    """Category index view marker interface"""
