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
from ztfy.blog.paragraphs.interfaces import IIllustrationInfo

# import Zope3 packages
from z3c.form import field

# import local packages
from ztfy.blog.browser.paragraph import BaseParagraphAddForm, BaseParagraphEditForm
from ztfy.blog.paragraphs.illustration import Illustration
from ztfy.i18n.browser import ztfy_i18n
from ztfy.skin.menu import JsMenuItem

from ztfy.blog import _


class IllustrationAddMenuItem(JsMenuItem):
    """Illustration add menu"""

    title = _(":: Add illustration...")

    def render(self):
        ztfy_i18n.need()
        return super(IllustrationAddMenuItem, self).render()


class IllustrationAddForm(BaseParagraphAddForm):
    """Illustration add form"""

    title = _("New illustration")
    legend = _("Adding new illustration")

    fields = field.Fields(IIllustrationInfo)
    handle_upload = True

    def create(self, data):
        return Illustration()


class IllustrationEditForm(BaseParagraphEditForm):
    """Illustration edit form"""

    legend = _("Edit illustration properties")

    fields = field.Fields(IIllustrationInfo)
    handle_upload = True
