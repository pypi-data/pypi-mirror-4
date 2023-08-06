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
from ztfy.blog.paragraphs.interfaces import ITextParagraphInfo

# import Zope3 packages
from z3c.form import field

# import local packages
from ztfy.blog.browser.paragraph import BaseParagraphAddForm, BaseParagraphEditForm
from ztfy.blog.paragraphs.text import TextParagraph
from ztfy.i18n.browser import ztfy_i18n
from ztfy.skin.menu import JsMenuItem

from ztfy.blog import _


class TextParagraphAddMenuItem(JsMenuItem):
    """Text paragraph add menu"""

    title = _(":: Add text paragraph...")

    def render(self):
        ztfy_i18n.need()
        return super(TextParagraphAddMenuItem, self).render()


class TextParagraphAddForm(BaseParagraphAddForm):
    """Text paragraph add form"""

    fields = field.Fields(ITextParagraphInfo)

    def updateWidgets(self):
        super(TextParagraphAddForm, self).updateWidgets()
        self.widgets['body'].rows = 12

    def create(self, data):
        return TextParagraph()


class TextParagraphEditForm(BaseParagraphEditForm):
    """Text paragraph edit form"""

    fields = field.Fields(ITextParagraphInfo)

    def updateWidgets(self):
        super(TextParagraphEditForm, self).updateWidgets()
        self.widgets['body'].rows = 12
