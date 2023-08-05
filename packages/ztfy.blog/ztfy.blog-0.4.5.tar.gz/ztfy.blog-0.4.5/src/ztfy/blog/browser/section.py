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
from zope.intid.interfaces import IIntIds
from zope.publisher.interfaces import NotFound

# import local interfaces
from ztfy.blog.browser.interfaces import ISectionAddFormMenuTarget, ITopicAddFormMenuTarget, \
                                         ISiteManagerTreeView
from ztfy.blog.browser.interfaces.container import IActionsColumn, IContainerTableViewActionsCell
from ztfy.blog.browser.interfaces.skin import ISectionIndexView
from ztfy.blog.interfaces import ISkinnable, IBaseContentRoles
from ztfy.blog.interfaces.section import ISection, ISectionInfo, ISectionContainer
from ztfy.skin.interfaces import IContainerBaseView
from ztfy.skin.layer import IZTFYBrowserLayer, IZTFYBackLayer

# import Zope3 packages
from z3c.form import field
from z3c.template.template import getLayoutTemplate
from zope.component import adapts, getUtility
from zope.i18n import translate
from zope.interface import implements
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.blog.browser.content import BaseContentDefaultBackViewAdapter
from ztfy.blog.browser.skin import BasePresentationEditForm, BaseIndexView, SkinSelectWidgetFactory
from ztfy.blog.section import Section
from ztfy.jqueryui import jquery_multiselect
from ztfy.security.browser import ztfy_security
from ztfy.security.browser.roles import RolesEditForm
from ztfy.skin.container import OrderedContainerBaseView
from ztfy.skin.form import AddForm, EditForm, DialogEditForm
from ztfy.skin.menu import MenuItem, JsMenuItem
from ztfy.utils.unicode import translateString

from ztfy.blog import _


class SectionTreeViewDefaultViewAdapter(BaseContentDefaultBackViewAdapter):

    adapts(ISection, IZTFYBackLayer, ISiteManagerTreeView)

    viewname = '@@contents.html'

    def getAbsoluteURL(self):
        intids = getUtility(IIntIds)
        return '++oid++%d/%s' % (intids.register(self.context), self.viewname)


class SectionContainerContentsViewMenu(MenuItem):
    """Sections container contents menu"""

    title = _("Section contents")


class SectionContainerContentsView(OrderedContainerBaseView):
    """Sections container contents view"""

    implements(ISectionAddFormMenuTarget, ITopicAddFormMenuTarget)

    legend = _("Container's sections")
    cssClasses = { 'table': 'orderable' }


class SectionContainerContentsViewCellActions(object):

    adapts(ISectionContainer, IZTFYBrowserLayer, IContainerBaseView, IActionsColumn)
    implements(IContainerTableViewActionsCell)

    def __init__(self, context, request, view, column):
        self.context = context
        self.request = request
        self.view = view
        self.column = column

    @property
    def content(self):
        container = ISectionContainer(self.context)
        if not (container.sections or container.topics):
            klass = "ui-workflow ui-icon ui-icon-trash"
            intids = getUtility(IIntIds)
            return '''<span class="%s" title="%s" onclick="$.ZTFY.container.remove(%s,this);"></span>''' % (klass,
                                                                                                            translate(_("Delete section"), context=self.request),
                                                                                                            intids.register(self.context))
        return ''


class SectionAddFormMenu(MenuItem):
    """Sections container add form menu"""

    title = _(" :: Add section...")


class SectionAddForm(AddForm):

    implements(ISectionAddFormMenuTarget)

    @property
    def title(self):
        return II18n(self.context).queryAttribute('title', request=self.request)

    legend = _("Adding new section")

    fields = field.Fields(ISectionInfo, ISkinnable)
    fields['skin'].widgetFactory = SkinSelectWidgetFactory

    def updateWidgets(self):
        super(SectionAddForm, self).updateWidgets()
        self.widgets['heading'].cols = 80
        self.widgets['heading'].rows = 10
        self.widgets['description'].cols = 80
        self.widgets['description'].rows = 3

    def create(self, data):
        section = Section()
        section.shortname = data.get('shortname', {})
        return section

    def add(self, section):
        language = II18n(self.context).getDefaultLanguage()
        name = translateString(section.shortname.get(language), forceLower=True, spaces='-')
        ids = list(self.context.keys()) + [name, ]
        self.context[name] = section
        self.context.updateOrder(ids)

    def nextURL(self):
        return '%s/@@contents.html' % absoluteURL(self.context, self.request)


class SectionEditForm(EditForm):

    legend = _("Section properties")

    fields = field.Fields(ISectionInfo, ISkinnable)
    fields['skin'].widgetFactory = SkinSelectWidgetFactory

    def updateWidgets(self):
        super(SectionEditForm, self).updateWidgets()
        self.widgets['heading'].cols = 80
        self.widgets['heading'].rows = 10
        self.widgets['description'].cols = 80
        self.widgets['description'].rows = 3


class SectionRolesMenuItem(JsMenuItem):
    """Section roles menu item"""

    title = _(":: Roles...")

    def update(self):
        ztfy_security.need()
        jquery_multiselect.need()
        super(SectionRolesMenuItem, self).update()


class SectionRolesEditForm(DialogEditForm, RolesEditForm):

    interfaces = (IBaseContentRoles,)
    layout = getLayoutTemplate()
    parent_interface = ISection


class SectionPresentationEditForm(BasePresentationEditForm):
    """Section presentation edit form"""

    legend = _("Edit section presentation properties")

    parent_interface = ISection


class BaseSectionIndexView(BaseIndexView):
    """Base section index view"""

    implements(ISectionIndexView)

    def update(self):
        if not self.context.visible:
            raise NotFound(self.context, 'index.html', self.request)
        super(BaseSectionIndexView, self).update()
        self.topics = self.context.getVisibleTopics()
