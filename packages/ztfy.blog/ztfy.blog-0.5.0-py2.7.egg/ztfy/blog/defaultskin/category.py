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
from ztfy.blog.browser.interfaces.skin import ICategoryIndexView

# import Zope3 packages
from zope.interface import implements

# import local packages
from ztfy.skin.page import TemplateBasedPage


class CategoryIndexView(TemplateBasedPage):
    """Category index page"""

    implements(ICategoryIndexView)

    def update(self):
        super(CategoryIndexView, self).update()
        self.topics = self.context.getVisibleTopics()

    def getTopics(self):
        page = int(self.request.form.get('page', 0))
        page_length = 10
        first = page_length * page
        last = first + page_length - 1
        pages = len(self.topics) / page_length
        if len(self.topics) % page_length:
            pages += 1
        return { 'topics': self.topics[first:last + 1],
                 'pages': pages,
                 'first': first,
                 'last': last,
                 'has_prev': page > 0,
                 'has_next': last < len(self.topics) - 1 }
