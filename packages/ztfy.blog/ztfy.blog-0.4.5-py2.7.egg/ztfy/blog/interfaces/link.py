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
from ztfy.blog.interfaces import IBaseContent
from ztfy.blog.interfaces.container import IOrderedContainer
from ztfy.i18n.interfaces import II18nAttributesAware

# import Zope3 packages
from zope.container.constraints import containers, contains
from zope.interface import Interface
from zope.schema import Object

# import local packages
from ztfy.blog.schema import InternalReference
from ztfy.i18n.schema import I18nText, I18nTextLine, Language

from ztfy.blog import _


#
# Links management
#

class ILinkNamespaceTarget(Interface):
    """Marker interface for targets handling '++links++' namespace traverser"""


class ILinkFormatter(Interface):
    """Link renderer interface"""

    def render():
        """Render link's HTML"""


class ILinkChecker(Interface):
    """Link visibility checker interface"""

    def canView():
        """Check link visibility"""


class IBaseLinkInfo(II18nAttributesAware):
    """Links base interface"""

    title = I18nTextLine(title=_("Title"),
                         description=_("Displayed link's title"),
                         required=False)

    description = I18nText(title=_("Description"),
                           description=_("Short description of provided link"),
                           required=False)

    language = Language(title=_("Link's target language"),
                        description=_("Actual language of link's target content"),
                        required=False)

    def getLink(request=None, view=None):
        """Get full link for given link"""


class IInternalLinkInfo(IBaseLinkInfo):
    """Internal link base interface"""

    target_oid = InternalReference(title=_("Link's target"),
                                   description=_("Internal ID of link's target"),
                                   required=True)

    target = Object(title=_("Link's target"),
                    schema=IBaseContent,
                    readonly=True)


class IInternalLink(IInternalLinkInfo, IContained):
    """Internal link interface"""

    containers('ztfy.blog.interfaces.link.ILinkContainer')


class IExternalLinkInfo(IBaseLinkInfo):
    """External link base interface"""

    url = I18nTextLine(title=_("URL"),
                       description=_("External URL ; maybe http:, https:, mailto:..."),
                       required=True)


class IExternalLink(IExternalLinkInfo, IContained):
    """External link interface"""

    containers('ztfy.blog.interfaces.link.ILinkContainer')


class ILinkContainer(IOrderedContainer, ILinkNamespaceTarget):
    """Links container interface"""

    contains(IBaseLinkInfo)

    def getVisibleLinks():
        """Get list of visible links"""


class ILinkContainerTarget(ILinkNamespaceTarget):
    """Marker interface for links container target"""
