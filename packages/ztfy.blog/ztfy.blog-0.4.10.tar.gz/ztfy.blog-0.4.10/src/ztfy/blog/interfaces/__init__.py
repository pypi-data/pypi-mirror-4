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

# import local interfaces
from ztfy.i18n.interfaces import II18nAttributesAware

# import Zope3 packages
from zope.interface import Interface, Attribute
from zope.schema import Choice, TextLine, List
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

# import local packages
from ztfy.i18n.schema import I18nTextLine, I18nText, I18nImage, I18nCthumbImage
from ztfy.security.schema import PrincipalList

from ztfy.blog import _


#
# Skinnable contents
#

class ISkinnable(Interface):

    skin = Choice(title=_("Skin name"),
                  description=_("Name of the skin applied to the current context ; WARNING: inheritance can only work correctly in specific contexts..."),
                  required=False,
                  vocabulary="ZTFY blog skins")

    def getSkin():
        """Get real skin applied to context"""


#
# Content base interface
#

class IUniqueID(Interface):
    """Interface for objects with unique ID"""

    oid = TextLine(title=_("Unique ID"),
                   description=_("Globally unique identifier of this content can be used to create internal links"),
                   readonly=True)


class IPathElements(Interface):
    """Interface used to index object's path"""

    paths = List(title=_("Path elements"),
                 description=_("List of path elements matching adapted object"),
                 value_type=TextLine())


class IBaseContentType(Interface):
    """Base content type interface"""

    content_type = Attribute(_("Content type"))


class IBaseContent(IBaseContentType, II18nAttributesAware):
    """Base content interface"""

    title = I18nTextLine(title=_("Title"),
                         description=_("Content title"),
                         required=True)

    shortname = I18nTextLine(title=_("Short name"),
                             description=_("Short name of the content can be displayed by several templates"),
                             required=True)

    description = I18nText(title=_("Description"),
                           description=_("Internal description included in HTML 'meta' headers"),
                           required=False)

    keywords = I18nTextLine(title=_("Keywords"),
                            description=_("A list of keywords matching content, separated by commas"),
                            required=False)

    header = I18nImage(title=_("Header image"),
                       description=_("This banner can be displayed by skins on page headers"),
                       required=False)

    heading = I18nText(title=_("Heading"),
                       description=_("Short header description of the content"),
                       required=False)

    illustration = I18nCthumbImage(title=_("Illustration"),
                                   description=_("This illustration can be displayed by several presentation templates"),
                                   required=False)

    illustration_title = I18nTextLine(title=_("Illustration alternate title"),
                                      description=_("This text will be used as an alternate title for the illustration"),
                                      required=False)


class IMainContent(Interface):
    """Marker element for first level site contents"""


class ITopicElement(Interface):
    """Marker interface for topics elements"""


class IBaseContentRoles(Interface):
    """Site manager roles"""

    administrators = PrincipalList(title=_("Site administrators"),
                                   description=_("List of site's administrators"),
                                   required=False)

    contributors = PrincipalList(title=_("Site contributors"),
                                 description=_("List of site's contributors"),
                                 required=False)


#
# Workflow management
#

STATUS_DRAFT = 0
STATUS_PUBLISHED = 1
STATUS_RETIRED = 2
STATUS_ARCHIVED = 3
STATUS_DELETED = 4

STATUS_IDS = [ 'draft', 'published', 'retired', 'archived', 'deleted' ]
STATUS_LABELS = (_("Draft"), _("Published"), _("Retired"), _("Archived"), _("Deleted"))

STATUS_VOCABULARY = SimpleVocabulary([SimpleTerm(i, i, t) for i, t in enumerate(STATUS_LABELS)])
