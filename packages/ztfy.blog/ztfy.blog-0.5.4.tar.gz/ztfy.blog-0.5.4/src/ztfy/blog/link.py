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
from zope.annotation.interfaces import IAnnotations
from zope.intid.interfaces import IIntIds

# import local interfaces
from ztfy.blog.interfaces.link import IBaseLinkInfo, IInternalLink, IExternalLink, ILinkContainer, ILinkContainerTarget, ILinkFormatter, ILinkChecker
from ztfy.workflow.interfaces import IWorkflowTarget, IWorkflowContent

# import Zope3 packages
from zope.component import adapter, getUtility, queryMultiAdapter
from zope.container.contained import Contained
from zope.interface import implementer, implements, Interface
from zope.location import locate
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.blog.ordered import OrderedContainer
from ztfy.i18n.property import I18nTextProperty
from ztfy.utils.request import getRequest
from ztfy.utils.traversing import getParent


class BaseLink(Persistent, Contained):

    title = I18nTextProperty(IBaseLinkInfo['title'])
    description = I18nTextProperty(IBaseLinkInfo['description'])
    language = FieldProperty(IBaseLinkInfo['language'])

    def getLink(self, request=None, view=None):
        if request is None:
            request = getRequest()
        if view is None:
            view = Interface
        adapter = queryMultiAdapter((self, request, view), ILinkFormatter)
        if adapter is not None:
            return adapter.render()
        return u''


class InternalLink(BaseLink):

    implements(IInternalLink, ILinkChecker)

    target_oid = FieldProperty(IInternalLink['target_oid'])

    @property
    def target(self):
        if not self.target_oid:
            return None
        intids = getUtility(IIntIds)
        return intids.queryObject(self.target_oid)

    def canView(self):
        """See `ILinkChecker` interface"""
        target = self.target
        if target is None:
            return False
        wf_parent = getParent(target, IWorkflowTarget)
        return (wf_parent is None) or IWorkflowContent(wf_parent).isVisible()

    def getLink(self, request=None, view=None):
        if not self.canView():
            return u''
        return super(InternalLink, self).getLink(request, view)


class ExternalLink(BaseLink):

    implements(IExternalLink, ILinkChecker)

    url = I18nTextProperty(IExternalLink['url'])

    def canView(self):
        """See `ILinkChecker` interface"""
        return True


class LinkContainer(OrderedContainer):

    implements(ILinkContainer)

    def getVisibleLinks(self):
        return [link for link in self.values() if ILinkChecker(link).canView()]


LINKS_ANNOTATION_KEY = 'ztfy.blog.link.container'

@adapter(ILinkContainerTarget)
@implementer(ILinkContainer)
def LinkContainerFactory(context):
    """Links container adapter"""
    annotations = IAnnotations(context)
    container = annotations.get(LINKS_ANNOTATION_KEY)
    if container is None:
        container = annotations[LINKS_ANNOTATION_KEY] = LinkContainer()
        locate(container, context, '++links++')
    return container
