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
from zope.container.interfaces import IContainer, IContained

# import local interfaces
from ztfy.i18n.interfaces import II18nAttributesAware

# import Zope3 packages
from zope.container.constraints import containers, contains
from zope.interface import Interface
from zope.schema import List, Object, Int

# import local packages
from ztfy.i18n.schema import I18nText, I18nTextLine

from ztfy.blog import _


#
# Categories management interfaces
#

class ICategoryInfo(II18nAttributesAware):
    """Marker interface used to handle circular references"""

    title = I18nTextLine(title=_("Title"),
                         description=_("Title of the category"),
                         required=True)

    shortname = I18nTextLine(title=_("Short name"),
                             description=_("Short name of the category"),
                             required=True)

    heading = I18nText(title=_("Heading"),
                       description=_("Short description of the category"),
                       required=False)

    def getCategoryIds():
        """Get IDs of category and sub-categories"""

    def getVisibleTopics():
        """Get list of visible topics matching this category"""


class ICategoryWriter(Interface):
    """Category writer interface"""


class ICategory(ICategoryInfo, ICategoryWriter, IContainer, IContained):
    """Category full interface"""

    contains('ztfy.blog.interfaces.category.ICategory')
    containers('ztfy.blog.interfaces.category.ICategory',
               'ztfy.blog.interfaces.category.ICategoryManager')


class ICategoryManager(ICategory):
    """Categories management interface"""


class ICategoryManagerTarget(Interface):
    """Marker interface for categories management"""


class ICategorizedContent(Interface):
    """Content catagory target interface"""

    categories = List(title=_("Categories"),
                      description=_("List of categories associated with this content"),
                      required=False,
                      default=[],
                      value_type=Object(schema=ICategory))

    categories_ids = List(title=_("Categories IDs"),
                          description=_("Internal IDs of content's categories, used for indexing"),
                          required=False,
                          readonly=True,
                          value_type=Int())


class ICategoriesTarget(Interface):
    """Marker interface for contents handling categories"""
