### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2009 Thierry Florac <tflorac AT ulthar.net>
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
from persistent import Persistent

# import Zope3 interfaces
from zope.annotation.interfaces import IAnnotations

# import local interfaces
from hurry.query.interfaces import IQuery
from ztfy.blog.interfaces.category import ICategory, ICategoryManager, ICategoryManagerTarget
from ztfy.blog.interfaces.category import ICategorizedContent, ICategoriesTarget

# import Zope3 packages
from zope.component import adapter, getUtility
from zope.container.folder import Folder
from zope.interface import implementer, implements, alsoProvides
from zope.intid.interfaces import IIntIds
from zope.location import locate
from zope.schema.fieldproperty import FieldProperty

# import local packages
from hurry.query.set import AnyOf
from ztfy.i18n.property import I18nTextProperty
from ztfy.workflow.interfaces import IWorkflowContent


class Category(Folder):
    """Category persistence class"""

    implements(ICategory)

    title = I18nTextProperty(ICategory['title'])
    shortname = I18nTextProperty(ICategory['shortname'])
    heading = I18nTextProperty(ICategory['heading'])

    def getCategoryIds(self):
        """See `ICategory` interface"""
        intids = getUtility(IIntIds)
        result = [intids.queryId(self), ]
        for category in self.values():
            result.extend(category.getCategoryIds())
        return result

    def getVisibleTopics(self):
        """See `ICategory` interface"""
        query = getUtility(IQuery)
        results = query.searchResults(AnyOf(('Catalog', 'categories'), self.getCategoryIds()))
        return sorted([v for v in results if IWorkflowContent(v).isVisible()],
                      key=lambda x: IWorkflowContent(x).publication_effective_date,
                      reverse=True)


CATEGORY_MANAGER_ANNOTATIONS_KEY = 'ztfy.blog.category.manager'

@adapter(ICategoryManagerTarget)
@implementer(ICategoryManager)
def CategoryManagerFactory(context):
    annotations = IAnnotations(context)
    manager = annotations.get(CATEGORY_MANAGER_ANNOTATIONS_KEY)
    if manager is None:
        manager = annotations[CATEGORY_MANAGER_ANNOTATIONS_KEY] = Category()
        alsoProvides(manager, ICategoryManager)
        locate(manager, context, '++category++')
    return manager



class CategoriesList(Persistent):
    """Content categories container"""

    implements(ICategorizedContent)

    categories = FieldProperty(ICategorizedContent['categories'])

    @property
    def categories_ids(self):
        intids = getUtility(IIntIds)
        return [intids.register(cat) for cat in self.categories]


CATEGORIES_ANNOTATIONS_KEY = 'ztfy.blog.category.content'

@adapter(ICategoriesTarget)
@implementer(ICategorizedContent)
def CategorizedContentFactory(context):
    """Content categories adapter"""
    annotations = IAnnotations(context)
    container = annotations.get(CATEGORIES_ANNOTATIONS_KEY)
    if container is None:
        container = annotations[CATEGORIES_ANNOTATIONS_KEY] = CategoriesList()
    return container
