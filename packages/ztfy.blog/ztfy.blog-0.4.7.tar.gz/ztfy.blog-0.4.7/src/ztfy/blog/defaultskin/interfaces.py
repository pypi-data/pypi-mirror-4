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
from ztfy.blog.interfaces import IBaseContent
from ztfy.blog.browser.interfaces.skin import IBasePresentationInfo
from ztfy.i18n.interfaces import II18nAttributesAware

# import Zope3 packages
from zope.interface import Interface, Attribute
from zope.schema import List, Choice, Bool, Int, TextLine, Object
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

# import local packages
from ztfy.i18n.schema import I18nTextLine

from ztfy.blog import _


HEADER_POSITION_LEFT = 0
HEADER_POSITION_TOP = 1

HEADER_POSITIONS = (_("Left column"),
                    _("Page top"))

HEADER_POSITIONS_VOCABULARY = SimpleVocabulary([SimpleTerm(v, t, t) for v, t in enumerate(HEADER_POSITIONS)])


class IDefaultPresentationInfo(IBasePresentationInfo):
    """Base interface for presentation infos"""

    header_format = Choice(title=_("Header format"),
                           description=_("Text format used for content's header"),
                           required=True,
                           default=u'zope.source.plaintext',
                           vocabulary='SourceTypes')

    header_position = Choice(title=_("Header position"),
                             description=_("Position of content's header"),
                             required=True,
                             default=HEADER_POSITION_LEFT,
                             vocabulary=HEADER_POSITIONS_VOCABULARY)

    display_googleplus = Bool(title=_("Display Google +1 button"),
                              description=_("Display Google +1 button next to content's title"),
                              required=True,
                              default=True)

    display_fb_like = Bool(title=_("Display Facebook 'like' button"),
                           description=_("Display Facebook 'like' button next to content's title"),
                           required=True,
                           default=True)


class ISiteManagerPresentationInfo(IDefaultPresentationInfo, II18nAttributesAware):
    """Site manager presentation info"""

    main_blogs = List(title=_("Main blogs"),
                      description=_("Summary of selected blogs last entries will be listed in front page"),
                      required=False,
                      unique=True,
                      default=[],
                      value_type=Choice(vocabulary="ZTFY site blogs"))

    nb_entries = Int(title=_("Entries count"),
                     description=_("Number of entries displayed in front page (if a blog is selected)"),
                     required=True,
                     default=10)

    owner = TextLine(title=_("Site's owner name"),
                     description=_("Site's owner name can be displayed on pages footers"),
                     required=False)

    owner_mailto = TextLine(title=_("Owner's mail address"),
                            description=_("""Mail address can be displayed on pages footer in a "mailto" link"""),
                            required=False)

    signature = I18nTextLine(title=_("Site's signature"),
                             description=_("Signature's complement to put on pages footers (can include HTML code)"),
                             required=False)

    facebook_app_id = TextLine(title=_("Facebook application ID"),
                               description=_("Application ID declared on Facebook"),
                               required=False)

    disqus_site_id = TextLine(title=_("Disqus site ID"),
                              description=_("Site's ID on Disqus comment platform can be used to allow topics comments"),
                              required=False)


class IBlogPresentationInfo(IDefaultPresentationInfo):
    """Blog presentation info"""

    page_entries = Int(title=_("Topics per page"),
                       description=_("Number of topics displayed into one page"),
                       required=True,
                       default=10)

    facebook_app_id = TextLine(title=_("Facebook application ID"),
                               description=_("Application ID declared on Facebook ; this attribute is not used if blog is contained insite a site manager"),
                               required=False)

    disqus_site_id = TextLine(title=_("Disqus site ID"),
                              description=_("Site's ID on Disqus comment platform can be used to allow topics comments ; this attribute is not used if blog is contained inside a site manager"),
                              required=False)


SECTION_DISPLAY_LIST = 0
SECTION_DISPLAY_FIRST = 1

SECTION_DISPLAY_MODES = (_("Display topics list"),
                         _("Display content of first published topic"))

SECTION_DISPLAY_VOCABULARY = SimpleVocabulary([SimpleTerm(i, t, t) for i, t in enumerate(SECTION_DISPLAY_MODES)])


class ISectionPresentationInfo(IDefaultPresentationInfo):
    """Section presentation info"""

    presentation_mode = Choice(title=_("Presentation mode"),
                               description=_("Select presentation mode for this section"),
                               required=True,
                               default=SECTION_DISPLAY_LIST,
                               vocabulary=SECTION_DISPLAY_VOCABULARY)


ILLUSTRATION_DISPLAY_NONE = 0
ILLUSTRATION_DISPLAY_LEFT = 1
ILLUSTRATION_DISPLAY_RIGHT = 2
ILLUSTRATION_DISPLAY_CENTER = 3

ILLUSTRATION_DISPLAY_MODES = (_("Don't display illustration"),
                              _("Display illustration as thumbnail on left side"),
                              _("Display illustration as thumbnail on right side"),
                              _("Display centered illustration"))

ILLUSTRATION_DISPLAY_VOCABULARY = SimpleVocabulary([SimpleTerm(i, t, t) for i, t in enumerate(ILLUSTRATION_DISPLAY_MODES)])


class ITopicPresentationInfo(IDefaultPresentationInfo):
    """Topic presentation info"""

    illustration_position = Choice(title=_("Illustration's position"),
                                   description=_("Select position of topic's illustration"),
                                   required=True,
                                   default=ILLUSTRATION_DISPLAY_LEFT,
                                   vocabulary=ILLUSTRATION_DISPLAY_VOCABULARY)

    linked_resources = List(title=_("Downloadable resources"),
                            description=_("Select list of resources displayed as download links"),
                            required=False,
                            default=[],
                            value_type=Choice(vocabulary="ZTFY content resources"))


class IContainerSitemapInfo(Interface):
    """Container sitemap info"""

    values = List(title=_("Container values"),
                  value_type=Object(schema=IBaseContent),
                  readonly=True)


class IBaseMeta(Interface):
    """Base meta header interface"""

    def render():
        """Render given meta header"""


class IHTTPEquivMetaHeader(IBaseMeta):
    """HTTP-Equiv meta header interface"""

    http_equiv = Attribute(_("HTTP equiv header"))

    value = Attribute(_("Meta content value"))


class IContentMetaHeader(IBaseMeta):
    """Content meta header interface"""

    name = Attribute(_("Meta name"))

    value = Attribute(_("Meta content value"))


class IPropertyMetaHeader(IBaseMeta):
    """Property meta header interface"""

    property = Attribute(_("Meta property"))

    value = Attribute(_("Meta content value"))


class ILinkMetaHeader(IBaseMeta):
    """Link meta header interface"""

    rel = Attribute(_("Meta rel attribute"))

    type = Attribute(_("Meta type attribute"))

    href = Attribute(_("Meta link target"))


class IContentMetasHeaders(Interface):
    """Content metas headers interface"""

    metas = List(title=_("Metas list"),
                 description=_("Full list of metas associated with this content"),
                 value_type=Object(schema=IContentMetaHeader))


class IPageMetasHeaders(Interface):
    """Full list of metas headers for given content"""

    metas = List(title=_("Metas list"),
                 description=_("Full list of metas associated with this content"),
                 value_type=Object(schema=IContentMetaHeader))
