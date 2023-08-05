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
from zope.container.interfaces import IContained

# import local interfaces
from ztfy.blog.interfaces.container import IOrderedContainer
from ztfy.i18n.interfaces import II18nAttributesAware

# import Zope3 packages
from zope.container.constraints import containers, contains
from zope.interface import Interface
from zope.schema import TextLine

# import local packages
from ztfy.file.schema import FileField
from ztfy.i18n.schema import I18nText, I18nTextLine, Language

from ztfy.blog import _


#
# Resources management
#

class IResourceNamespaceTarget(Interface):
    """Marker interface for targets handling '++static++' namespace traverser"""


class IResourceInfo(II18nAttributesAware):
    """Static resources base interface"""

    title = I18nTextLine(title=_("Title"),
                         description=_("Name of the resource"),
                         required=False)

    description = I18nText(title=_("Description"),
                           description=_("Short description of resource content"),
                           required=False)

    content = FileField(title=_("Resource data"),
                        description=_("Current content of the given external resource"),
                        required=True)

    filename = TextLine(title=_("Filename"),
                        description=_("Resource's public filename"),
                        required=False)

    language = Language(title=_("Resource language"),
                        description=_("Actual language of the resource"),
                        required=False)


class IResource(IResourceInfo, IContained):
    """Static resource interface"""

    containers('ztfy.blog.interfaces.resource.IResourceContainer')


class IResourceContainer(IOrderedContainer, IResourceNamespaceTarget):
    """Static resources container interface"""

    contains(IResource)


class IResourceContainerTarget(IResourceNamespaceTarget):
    """Marker interface for static resources container target"""
