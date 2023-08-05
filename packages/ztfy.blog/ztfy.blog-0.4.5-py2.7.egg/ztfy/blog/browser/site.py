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

# import Zope3 interfaces
from z3c.table.interfaces import INoneCell
from zope.intid.interfaces import IIntIds

# import local interfaces
from ztfy.blog.browser.interfaces import ISiteManagerTreeView, ISiteManagerTreeViewContent, IBlogAddFormMenuTarget, ISectionAddFormMenuTarget
from ztfy.blog.browser.interfaces.container import ITitleColumn, IActionsColumn, IContainerTableViewActionsCell
from ztfy.blog.browser.interfaces.container import IContainerTableViewTitleCell
from ztfy.blog.browser.interfaces.skin import ISiteManagerIndexView
from ztfy.blog.interfaces import IBaseContent, IBaseContentRoles, ISkinnable
from ztfy.blog.interfaces.blog import IBlog
from ztfy.blog.interfaces.section import ISection
from ztfy.blog.interfaces.site import ISiteManager, ISiteManagerInfo, ISiteManagerBackInfo, \
                                      ITreeViewContents
from ztfy.blog.interfaces.topic import ITopic
from ztfy.skin.interfaces import IContainerBaseView
from ztfy.skin.layer import IZTFYBrowserLayer, IZTFYBackLayer

# import Zope3 packages
from z3c.form import field
from z3c.template.template import getLayoutTemplate
from zope.component import adapts, getUtility
from zope.interface import implements, Interface
from zope.traversing import namespace

# import local packages
from ztfy.blog.browser.content import BaseContentDefaultBackViewAdapter
from ztfy.blog.browser.skin import BasePresentationEditForm, \
                                   BaseIndexView, SkinSelectWidgetFactory
from ztfy.jqueryui import jquery_treetable, jquery_multiselect, jquery_ui_base
from ztfy.security.browser import ztfy_security
from ztfy.security.browser.roles import RolesEditForm
from ztfy.skin.container import ContainerBaseView, OrderedContainerBaseView
from ztfy.skin.form import EditForm, DialogEditForm
from ztfy.skin.menu import MenuItem, JsMenuItem

from ztfy.blog import _


class SiteManagerTreeViewMenu(MenuItem):
    """Site manager tree view menu"""

    title = _("Tree view")


def getValues(parent, context, output):
    output.append((parent, context))
    contents = ITreeViewContents(context, None)
    if contents is not None:
        for item in contents.values:
            getValues(context, item, output)


class SiteManagerTreeView(ContainerBaseView):
    """Site manager tree view"""

    implements(ISiteManagerTreeView)

    sortOn = None
    cssClasses = { 'table': 'orderable treeview' }
    batchSize = 10000
    startBatchingAt = 10000

    def __init__(self, context, request):
        super(SiteManagerTreeView, self).__init__(context, request)
        self.intids = getUtility(IIntIds)

    @property
    def values(self):
        result = []
        getValues(None, self.context, result)
        return result

    def renderRow(self, row, cssClass=None):
        isSelected = self.isSelectedRow(row)
        if isSelected and self.cssClassSelected and cssClass:
            cssClass = '%s %s' % (self.cssClassSelected, cssClass)
        elif isSelected and self.cssClassSelected:
            cssClass = self.cssClassSelected
        (parent, context), _col, _colspan = row[0]
        content = ISiteManagerTreeViewContent(context, None)
        if (content is not None) and content.resourceLibrary:
            content.resourceLibrary.need()
        if (content is not None) and content.cssClass:
            cssClass += ' %s' % content.cssClass
        else:
            if ISiteManager.providedBy(context):
                cssClass += ' site'
            elif IBlog.providedBy(context):
                cssClass += ' blog'
            elif ISection.providedBy(context):
                cssClass += ' section'
            elif ITopic.providedBy(context):
                cssClass += ' topic'
        if parent is not None:
            cssClass += ' child-of-node-%d' % self.intids.register(parent)
        id = 'id="node-%d"' % self.intids.register(context)
        cssClass = self.getCSSClass('tr', cssClass)
        cells = [self.renderCell(context, col, colspan)
                 for (parent, context), col, colspan in row]
        return u'\n    <tr %s%s>%s\n    </tr>' % (id, cssClass, u''.join(cells))

    def renderCell(self, item, column, colspan=0):
        if INoneCell.providedBy(column):
            return u''
        cssClass = column.cssClasses.get('td')
        cssClass = self.getCSSClass('td', cssClass)
        colspanStr = colspan and ' colspan="%s"' % colspan or ''
        return u'\n      <td%s%s>%s</td>' % (cssClass, colspanStr, column.renderCell(item))

    def update(self):
        super(SiteManagerTreeView, self).update()
        jquery_treetable.need()
        jquery_ui_base.need()


class SiteManagerTreeViewTitleColumnCellAdapter(object):

    adapts(IBaseContent, IZTFYBrowserLayer, ISiteManagerTreeView, ITitleColumn)
    implements(IContainerTableViewTitleCell)

    prefix = u''
    after = u''
    suffix = u''

    def __init__(self, context, request, table, column):
        self.context = context
        self.request = request
        self.table = table
        self.column = column

    @property
    def before(self):
        return '<span class="ui-icon"></span>'


class SiteManagerContentsViewMenu(MenuItem):
    """Site manager contents view menu"""

    title = _("Site contents")


class SiteManagerContentsView(OrderedContainerBaseView):
    """Site manager contents view"""

    implements(IBlogAddFormMenuTarget, ISectionAddFormMenuTarget)

    legend = _("Site's content")
    cssClasses = { 'table': 'orderable' }

    @property
    def values(self):
        return ISiteManager(self.context).values()


class SiteManagerContentsViewCellActions(object):

    adapts(ISiteManager, IZTFYBrowserLayer, IContainerBaseView, IActionsColumn)
    implements(IContainerTableViewActionsCell)

    def __init__(self, context, request, view, column):
        self.context = context
        self.request = request
        self.view = view
        self.column = column

    @property
    def content(self):
        return u''


class SiteManagerEditForm(EditForm):

    legend = _("Site manager properties")

    fields = field.Fields(ISiteManagerInfo, ISkinnable)
    fields['skin'].widgetFactory = SkinSelectWidgetFactory

    def updateWidgets(self):
        super(SiteManagerEditForm, self).updateWidgets()
        self.widgets['heading'].cols = 80
        self.widgets['heading'].rows = 10
        self.widgets['description'].cols = 80
        self.widgets['description'].rows = 3


class SiteManagerRolesMenuItem(JsMenuItem):
    """Site manager roles menu item"""

    title = _(":: Roles...")

    def update(self):
        super(SiteManagerRolesMenuItem, self).update()
        ztfy_security.need()
        jquery_multiselect.need()


class SiteManagerRolesEditForm(DialogEditForm, RolesEditForm):

    interfaces = (IBaseContentRoles,)
    layout = getLayoutTemplate()
    parent_interface = ISiteManager


class SiteManagerBackInfoMenuItem(JsMenuItem):
    """Site manager back-office infos menu item"""

    title = _(":: Back-office...")


class SiteManagerBackInfoEditForm(DialogEditForm):
    """Site manager back-office infos edit form"""

    legend = _("Edit back-office properties")

    fields = field.Fields(ISiteManagerBackInfo)

    def getContent(self):
        return ISiteManagerBackInfo(self.context)


class SiteManagerBackInfoNamespace(namespace.view):
    """++back++ namespace traverser"""

    def traverse(self, name, ignored):
        return ISiteManagerBackInfo(self.context)


class SiteManagerPresentationEditForm(BasePresentationEditForm):
    """Site manager presentation edit form"""

    legend = _("Edit site presentation properties")

    parent_interface = ISiteManager


class SiteManagerDefaultViewAdapter(BaseContentDefaultBackViewAdapter):

    adapts(ISiteManager, IZTFYBackLayer, Interface)

    viewname = '@@treeview.html'


class SiteManagerTreeViewDefaultViewAdapter(SiteManagerDefaultViewAdapter):

    adapts(ISiteManager, IZTFYBackLayer, ISiteManagerTreeView)

    viewname = '@@properties.html'


class BaseSiteManagerIndexView(BaseIndexView):
    """Base site manager index view"""

    implements(ISiteManagerIndexView)
