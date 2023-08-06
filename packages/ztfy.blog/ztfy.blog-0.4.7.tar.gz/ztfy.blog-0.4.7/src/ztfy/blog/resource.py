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
from persistent import Persistent

# import Zope3 interfaces
from z3c.language.switch.interfaces import II18n
from zope.annotation.interfaces import IAnnotations
from zope.schema.interfaces import IVocabularyFactory

# import local interfaces
from ztfy.blog.interfaces.resource import IResource, IResourceContainer, IResourceContainerTarget

# import Zope3 packages
from zope.component import adapter
from zope.container.contained import Contained
from zope.interface import implementer, implements, classProvides
from zope.location import locate
from zope.schema.fieldproperty import FieldProperty
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.security.proxy import removeSecurityProxy
from zope.traversing.api import getName

# import local packages
from ztfy.blog.ordered import OrderedContainer
from ztfy.extfile.blob import BlobFile, BlobImage
from ztfy.file.property import FileProperty
from ztfy.i18n.property import I18nTextProperty
from ztfy.utils.traversing import getParent


class Resource(Persistent, Contained):

    implements(IResource)

    title = I18nTextProperty(IResource['title'])
    description = I18nTextProperty(IResource['description'])
    content = FileProperty(IResource['content'], klass=BlobFile, img_klass=BlobImage)
    filename = FieldProperty(IResource['filename'])
    language = FieldProperty(IResource['language'])


class ResourceContainer(OrderedContainer):

    implements(IResourceContainer)


RESOURCES_ANNOTATIONS_KEY = 'ztfy.blog.resource.container'

@adapter(IResourceContainerTarget)
@implementer(IResourceContainer)
def ResourceContainerFactory(context):
    """Resources container adapter"""
    annotations = IAnnotations(context)
    container = annotations.get(RESOURCES_ANNOTATIONS_KEY)
    if container is None:
        container = annotations[RESOURCES_ANNOTATIONS_KEY] = ResourceContainer()
        locate(container, context, '++static++')
    return container


class ResourceContainerResourcesVocabulary(SimpleVocabulary):
    """List of resources of a given content"""

    classProvides(IVocabularyFactory)

    def __init__(self, context):
        container = getParent(context, IResourceContainerTarget)
        terms = [SimpleTerm(removeSecurityProxy(r), getName(r), II18n(r).queryAttribute('title') or '{{ %s }}' % r.filename) for r in IResourceContainer(container).values()]
        super(ResourceContainerResourcesVocabulary, self).__init__(terms)
