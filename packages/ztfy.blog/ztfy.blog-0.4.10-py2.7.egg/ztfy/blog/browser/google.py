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
from ztfy.blog.interfaces.google import IGoogleAnalytics, IGoogleAdSense
from ztfy.blog.interfaces.site import ISiteManager

# import Zope3 packages
from z3c.form import field
from z3c.template.template import getLayoutTemplate

# import local packages
from ztfy.skin.form import DialogEditForm
from ztfy.skin.menu import JsMenuItem

from ztfy.blog import _


class GoogleAnalyticsMenuItem(JsMenuItem):
    """Google Analytics menu item"""

    title = _(":: Google Analytics account...")


class GoogleAnalyticsEditForm(DialogEditForm):
    """Google Analytics edit form"""

    legend = _("Edit Google Analytics properties")

    fields = field.Fields(IGoogleAnalytics)
    layout = getLayoutTemplate()
    parent_interface = ISiteManager


class GoogleAdSenseMenuItem(JsMenuItem):
    """Google AdSense menu item"""

    title = _(":: Google AdSense account...")


class GoogleAdSenseEditForm(DialogEditForm):
    """Google AdSense edit form"""

    legend = _("Edit Google AdSense properties")

    fields = field.Fields(IGoogleAdSense)
    layout = getLayoutTemplate()
    parent_interface = ISiteManager
