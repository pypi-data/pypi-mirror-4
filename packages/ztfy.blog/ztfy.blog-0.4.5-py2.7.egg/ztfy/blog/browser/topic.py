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
from hurry.workflow.interfaces import IWorkflowState
from z3c.language.switch.interfaces import II18n
from zope.intid.interfaces import IIntIds
from zope.dublincore.interfaces import IZopeDublinCore
from zope.publisher.interfaces import NotFound

# import local interfaces
from ztfy.blog.browser.interfaces import ITopicAddFormMenuTarget, ISiteManagerTreeView
from ztfy.blog.browser.interfaces.container import IStatusColumn, IActionsColumn
from ztfy.blog.browser.interfaces.container import IContainerTableViewStatusCell, IContainerTableViewActionsCell
from ztfy.blog.browser.interfaces.skin import ITopicIndexView
from ztfy.blog.browser.interfaces.paragraph import IParagraphRenderer
from ztfy.blog.interfaces import STATUS_LABELS, STATUS_DRAFT, STATUS_RETIRED, STATUS_ARCHIVED
from ztfy.blog.interfaces.topic import ITopic, ITopicInfo, ITopicContainer
from ztfy.comment.interfaces import IComments
from ztfy.skin.interfaces import IContainerBaseView
from ztfy.skin.layer import IZTFYBrowserLayer, IZTFYBackLayer
from ztfy.workflow.interfaces import IWorkflowTarget, IWorkflowContent

# import Zope3 packages
from z3c.form import field
from zope.component import adapts, getUtility, queryMultiAdapter
from zope.i18n import translate
from zope.interface import implements
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.blog.browser.content import BaseContentDefaultBackViewAdapter
from ztfy.blog.browser.skin import BasePresentationEditForm, BaseIndexView
from ztfy.blog.topic import Topic
from ztfy.security.search import getPrincipal
from ztfy.skin.container import OrderedContainerBaseView
from ztfy.skin.form import AddForm, EditForm
from ztfy.skin.menu import MenuItem
from ztfy.skin.viewlets.properties import PropertiesViewlet
from ztfy.utils.timezone import tztime

from ztfy.blog import _


class TopicContainerContentsViewMenu(MenuItem):
    """Topics container contents menu"""

    title = _("Topics")


class TopicAddFormMenu(MenuItem):
    """Topics container add form menu"""

    title = _(" :: Add topic...")


class TopicTreeViewDefaultViewAdapter(BaseContentDefaultBackViewAdapter):

    adapts(ITopic, IZTFYBackLayer, ISiteManagerTreeView)

    def getAbsoluteURL(self):
        intids = getUtility(IIntIds)
        return '++oid++%d/%s' % (intids.register(self.context), self.viewname)


class TopicContainerContentsView(OrderedContainerBaseView):
    """Topics container contents view"""

    implements(ITopicAddFormMenuTarget)

    legend = _("Container's topics")
    cssClasses = { 'table': 'orderable' }

    @property
    def values(self):
        return ITopicContainer(self.context).topics


class TopicContainerTableViewCellStatus(object):

    adapts(ITopic, IZTFYBrowserLayer, IContainerBaseView, IStatusColumn)
    implements(IContainerTableViewStatusCell)

    def __init__(self, context, request, view, table):
        self.context = context
        self.request = request
        self.view = view
        self.table = table

    @property
    def content(self):
        status = IWorkflowState(self.context).getState()
        if status == STATUS_DRAFT:
            klass = "ui-workflow ui-icon ui-icon-draft"
        elif status == STATUS_RETIRED:
            klass = "ui-workflow ui-icon ui-icon-retired"
        elif status == STATUS_ARCHIVED:
            klass = "ui-workflow ui-icon ui-icon-archived"
        else:
            klass = "ui-workflow ui-icon ui-icon-published"
        if klass:
            return '<span class="%s"></span> %s' % (klass,
                                                    translate(STATUS_LABELS[status], context=self.request))
        return ''


class TopicContainerTableViewCellActions(object):

    adapts(ITopic, IZTFYBrowserLayer, IContainerBaseView, IActionsColumn)
    implements(IContainerTableViewActionsCell)

    def __init__(self, context, request, view, column):
        self.context = context
        self.request = request
        self.view = view
        self.column = column

    @property
    def content(self):
        status = IWorkflowState(self.context).getState()
        if status == STATUS_DRAFT:
            klass = "ui-workflow ui-icon ui-icon-trash"
            intids = getUtility(IIntIds)
            return '''<span class="%s" title="%s" onclick="$.ZTFY.container.remove(%s,this);"></span>''' % (klass,
                                                                                                            translate(_("Delete topic"), context=self.request),
                                                                                                            intids.register(self.context))
        return ''


class TopicAddForm(AddForm):

    implements(ITopicAddFormMenuTarget)

    @property
    def title(self):
        return II18n(self.context).queryAttribute('title', request=self.request)

    legend = _("Adding new topic")

    fields = field.Fields(ITopicInfo).omit('publication_year', 'publication_month') + \
             field.Fields(IWorkflowTarget)

    def updateWidgets(self):
        super(TopicAddForm, self).updateWidgets()
        self.widgets['heading'].cols = 80
        self.widgets['heading'].rows = 10
        self.widgets['description'].cols = 80
        self.widgets['description'].rows = 3

    def create(self, data):
        topic = Topic()
        topic.shortname = data.get('shortname', {})
        topic.workflow_name = data.get('workflow_name')
        return topic

    def add(self, topic):
        self.context.addTopic(topic)

    def nextURL(self):
        return '%s/@@contents.html' % absoluteURL(self.context, self.request)


class TopicEditForm(EditForm):

    legend = _("Topic properties")

    fields = field.Fields(ITopicInfo).omit('publication_year', 'publication_month')

    def updateWidgets(self):
        super(TopicEditForm, self).updateWidgets()
        self.widgets['heading'].cols = 80
        self.widgets['heading'].rows = 10
        self.widgets['description'].cols = 80
        self.widgets['description'].rows = 3


class TopicPresentationEditForm(BasePresentationEditForm):
    """Blog presentation edit form"""

    legend = _("Edit topic presentation properties")

    parent_interface = ITopic


class TopicPropertiesViewlet(PropertiesViewlet):
    """Topic properties viewlet"""

    @property
    def contributors(self):
        uids = IZopeDublinCore(self.context).creators[1:]
        return ', '.join((getPrincipal(uid).title for uid in uids))

    @property
    def status_date(self):
        return tztime(IWorkflowContent(self.context).state_date)

    @property
    def status_principal(self):
        return getPrincipal(IWorkflowContent(self.context).state_principal)

    @property
    def first_publication_date(self):
        return tztime(IWorkflowContent(self.context).first_publication_date)

    @property
    def publication_dates(self):
        content = IWorkflowContent(self.context)
        return (tztime(content.publication_effective_date), tztime(content.publication_expiration_date))

    @property
    def history(self):
        comments = IComments(self.context)
        return comments.getComments('__workflow__')


class BaseTopicIndexView(BaseIndexView):
    """Base topic index view"""

    implements(ITopicIndexView)

    def update(self):
        if not IWorkflowContent(self.context).isVisible():
            raise NotFound(self.context, self.__name__, self.request)
        super(BaseTopicIndexView, self).update()
        self.renderers = [renderer for renderer in [ queryMultiAdapter((paragraph, self, self.request), IParagraphRenderer)
                                                     for paragraph in self.context.getVisibleParagraphs(self.request) ]
                                                if renderer is not None]
        [renderer.update() for renderer in self.renderers]
