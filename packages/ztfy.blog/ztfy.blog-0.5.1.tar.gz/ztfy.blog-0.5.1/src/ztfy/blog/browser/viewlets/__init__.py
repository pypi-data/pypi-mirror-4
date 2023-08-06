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
from ztfy.blog.browser.interfaces.skin import IBaseViewlet, IPresentationTarget
from ztfy.blog.interfaces.site import ISiteManager

# import Zope3 packages
from zope.component import queryMultiAdapter
from zope.interface import implements

# import local packages
from ztfy.skin.viewlet import ViewletBase
from ztfy.utils.traversing import getParent


class BaseViewlet(ViewletBase):
    """Base viewlet class"""

    implements(IBaseViewlet)

    presentation_target = ISiteManager
    presentation = None

    @property
    def presentation_context(self):
        target = self.presentation_target
        if target is not None:
            return getParent(self.context, target)

    def update(self):
        super(BaseViewlet, self).update()
        context = self.presentation_context
        if context is not None:
            adapter = queryMultiAdapter((context, self.request, self), IPresentationTarget)
            if adapter is None:
                adapter = queryMultiAdapter((context, self.request), IPresentationTarget)
            if adapter is not None:
                interface = adapter.target_interface
                self.presentation = interface(context)
