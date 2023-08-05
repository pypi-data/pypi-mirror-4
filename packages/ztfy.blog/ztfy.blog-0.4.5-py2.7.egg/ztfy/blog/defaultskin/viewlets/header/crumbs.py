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
from z3c.language.switch.interfaces import II18n
from zope.dublincore.interfaces import IZopeDublinCore

# import local interfaces
from hurry.workflow.interfaces import IWorkflowState
from ztfy.blog.interfaces import STATUS_DELETED
from ztfy.skin.interfaces import IBreadcrumbInfo, IDefaultView

# import Zope3 packages
from zope.component import queryMultiAdapter
from zope.traversing.browser import absoluteURL
from zope.traversing.api import getParents

# import local packages
from ztfy.skin.viewlet import ViewletBase


class BreadcrumbsViewlet(ViewletBase):

    viewname = ''

    @property
    def crumbs(self):
        result = []
        state = IWorkflowState(self.context, None)
        if (state is None) or (state.getState() != STATUS_DELETED):
            for parent in reversed([self.context, ] + getParents(self.context)):
                value = None
                info = queryMultiAdapter((parent, self.request, self.__parent__), IBreadcrumbInfo)
                if info is not None:
                    if info.visible:
                        value = { 'title': info.title,
                                  'path': info.path }
                else:
                    visible = getattr(parent, 'visible', True)
                    if visible:
                        i18n = II18n(parent, None)
                        if i18n is not None:
                            name = i18n.queryAttribute('shortname', request=self.request) or i18n.queryAttribute('title', request=self.request)
                        else:
                            name = IZopeDublinCore(parent).title
                        if name:
                            adapter = queryMultiAdapter((parent, self.request, self.__parent__), IDefaultView)
                            if (adapter is not None) and adapter.viewname:
                                self.viewname = '/' + adapter.viewname
                            value = { 'title': name,
                                      'path': '%s%s' % (absoluteURL(parent, request=self.request),
                                                        self.viewname) }
                if value:
                    if result and (value['title'] == result[-1]['title']):
                        result[-1] = value
                    else:
                        result.append(value)
        return result
