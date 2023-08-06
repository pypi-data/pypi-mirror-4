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
from ztfy.blog.interfaces import ITopicElement
from ztfy.blog.interfaces.container import IOrderedContainer
from ztfy.i18n.interfaces import II18nAttributesAware

# import Zope3 packages
from zope.container.constraints import containers, contains
from zope.interface import Interface
from zope.schema import Bool, List, Object

# import local packages
from ztfy.i18n.schema import I18nText, I18nTextLine

from ztfy.blog import _


class IParagraphInfo(II18nAttributesAware):
    """Paragraph base interface"""

    title = I18nTextLine(title=_("Title"),
                         description=_("Paragraph title"),
                         required=False)

    heading = I18nText(title=_("Heading"),
                       description=_("Short header description of the paragraph"),
                       required=False)

    visible = Bool(title=_("Visible ?"),
                   description=_("Check to keep paragraph visible..."),
                   default=True,
                   required=True)


class IParagraphWriter(Interface):
    """Paragraph writer interface"""


class IParagraph(IParagraphInfo, IParagraphWriter, ITopicElement):
    """Paragraph full interface"""

    containers('ztfy.blog.interfaces.paragraph.IParagraphContainer')


class IParagraphContainerInfo(Interface):
    """Paragraph container base interface"""

    paragraphs = List(title=_("Paragraphs list"),
                      value_type=Object(schema=IParagraph),
                      readonly=True)

    def getVisibleParagraphs(request):
        """Get list of paragraphs visible from given request"""


class IParagraphContainer(IParagraphContainerInfo, IOrderedContainer):
    """Paragraph container interface"""

    contains(IParagraph)
