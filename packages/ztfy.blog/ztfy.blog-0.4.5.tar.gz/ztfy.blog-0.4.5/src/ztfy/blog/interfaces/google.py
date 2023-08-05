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
from zope.interface import Interface
from zope.schema import Bool, Int, TextLine, Choice
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

# import local packages

from ztfy.blog import _


class IGoogleAnalytics(Interface):
    """Google analytics interface"""

    enabled = Bool(title=_("Activate Google analytics ?"),
                   description=_("Are Google analytics statistics activated ?"),
                   required=True,
                   default=False)

    website_id = TextLine(title=_("Web site ID"),
                          description=_("Google analytics web site ID"),
                          required=False)

    verification_code = TextLine(title=_("Web site verification code"),
                                 description=_("Google site verification code"),
                                 required=False)


BOTTOM = 0
BOTTOM_TOPICS = 1
TOP = 2
TOP_TOPICS = 3

SLOT_POSITIONS_LABELS = (_("Bottom (all pages)"),
                         _("Bottom (topics only)"),
                         _("Top (all pages)"),
                         _("Top (topics only"))

SLOT_POSITIONS = SimpleVocabulary([SimpleTerm(i, i, t) for i, t in enumerate(SLOT_POSITIONS_LABELS)])


class IGoogleAdSense(Interface):
    """GoogleAds interface"""

    enabled = Bool(title=_("Activate Google AdSense ?"),
                   description=_("Integrate GoogleAdSense into your web site ?"),
                   required=True,
                   default=False)

    client_id = TextLine(title=_("Client ID"),
                         description=_("Google AdSense client ID"),
                         required=False)

    slot_id = TextLine(title=_("Slot ID"),
                       description=_("ID of the selected slot"),
                       required=False)

    slot_width = Int(title=_("Slot width"),
                     description=_("Width of the selected slot, in pixels"),
                     required=False)

    slot_height = Int(title=_("Slot height"),
                      description=_("Height of the selected slot, in pixels"),
                      required=False)

    slot_position = Choice(title=_("Slot position"),
                           description=_("Position of the selected slot in the generated pages"),
                           vocabulary=SLOT_POSITIONS,
                           default=BOTTOM,
                           required=True)

    def display(context, position):
        """Return boolean value to say if content provider should be displayed"""
