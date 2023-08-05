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
from ztfy.blog.paragraphs.interfaces import IHTMLParagraphInfo

# import Zope3 packages
from z3c.form import field

# import local packages
from ztfy.blog.browser.paragraph import BaseParagraphAddForm, BaseParagraphEditForm
from ztfy.blog.paragraphs.html import HTMLParagraph
from ztfy.i18n.browser import ztfy_i18n
from ztfy.jqueryui import jquery_tinymce
from ztfy.skin.menu import JsMenuItem

from ztfy.blog import _


class HTMLParagraphAddMenuItem(JsMenuItem):
    """HTML paragraph add menu"""

    title = _(":: Add HTML paragraph...")

    def render(self):
        ztfy_i18n.need()
        jquery_tinymce.need()
        return super(HTMLParagraphAddMenuItem, self).render()


class HTMLParagraphAddForm(BaseParagraphAddForm):
    """HTML paragraph add form"""

    fields = field.Fields(IHTMLParagraphInfo)

    def updateWidgets(self):
        super(HTMLParagraphAddForm, self).updateWidgets()
        self.widgets['body'].rows = 15

    def create(self, data):
        return HTMLParagraph()


class HTMLParagraphEditForm(BaseParagraphEditForm):
    """HTML paragraph edit form"""

    fields = field.Fields(IHTMLParagraphInfo)

    def updateWidgets(self):
        super(HTMLParagraphEditForm, self).updateWidgets()
        self.widgets['body'].rows = 15
