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
from ztfy.blog.paragraphs.interfaces import ICodeParagraphInfo

# import Zope3 packages
from z3c.form import field

# import local packages
from ztfy.blog.browser.paragraph import BaseParagraphAddForm, BaseParagraphEditForm
from ztfy.blog.paragraphs.code import CodeParagraph
from ztfy.i18n.browser import ztfy_i18n
from ztfy.skin.menu import JsMenuItem

from ztfy.blog import _


class CodeParagraphAddMenuItem(JsMenuItem):
    """Code paragraph add menu"""

    title = _(":: Add code paragraph...")

    def render(self):
        ztfy_i18n.need()
        return super(CodeParagraphAddMenuItem, self).render()


class CodeParagraphAddForm(BaseParagraphAddForm):
    """Code paragraph add form"""

    fields = field.Fields(ICodeParagraphInfo)

    def updateWidgets(self):
        super(CodeParagraphAddForm, self).updateWidgets()
        self.widgets['body'].rows = 15

    def create(self, data):
        return CodeParagraph()


class CodeParagraphEditForm(BaseParagraphEditForm):
    """Code paragraph edit form"""

    fields = field.Fields(ICodeParagraphInfo)

    def updateWidgets(self):
        super(CodeParagraphEditForm, self).updateWidgets()
        self.widgets['body'].rows = 15
