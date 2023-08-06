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
from ztfy.blog.browser import ztfy_blog_back

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces
from z3c.form.interfaces import IWidgets, ISubForm
from z3c.json.interfaces import IJSONWriter

# import local interfaces
from hurry.workflow.interfaces import IWorkflowInfo
from ztfy.blog.interfaces.topic import ITopicContainer
from ztfy.comment.interfaces import IComment

# import Zope3 packages
from z3c.form import field, button
from z3c.formjs import ajax, jsaction
from zope.component import getUtility, getMultiAdapter
from zope.i18n import translate
from zope.interface import implements, Interface
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.skin.form import EditForm
from ztfy.utils.traversing import getParent
from ztfy.workflow.interfaces import IWorkflowContentInfo

from ztfy.blog import _


class IWorkflowFormButtons(Interface):
    submit = button.Button(title=_("Submit"))


class WorkflowCommentAddForm(EditForm):
    """Workflow comment add form"""

    implements(ISubForm)

    legend = _("Workflow comment")

    fields = field.Fields(IComment).select('body')
    prefix = 'comment'

    def updateWidgets(self):
        self.widgets = getMultiAdapter((self, self.request, self.getContent()), IWidgets)
        self.widgets.ignoreContext = True
        self.widgets.update()


class WorkflowBaseForm(EditForm):
    """Workflow base form"""

    _done = False

    transition = None
    buttons = button.Buttons(IWorkflowFormButtons)
    prefix = 'workflow'

    @property
    def legend(self):
        return self.transition.title

    @property
    def help(self):
        return translate(self.transition.user_data.get('html_help'), context=self.request)

    def createSubForms(self):
        self.comment = WorkflowCommentAddForm(None, self.request)
        return [self.comment, ]

    def updateWidgets(self):
        super(WorkflowBaseForm, self).updateWidgets()
        self.buttons['submit'].title = self.transition.title
        self.comment.widgets['body'].required = False

    @button.handler(buttons['submit'])
    def submit(self, action):
        self.handleApply(self, action)
        if self.status != self.formErrorsMessage:
            self._next = self.nextURL()
            comments, _errors = self.comment.widgets.extract()
            info = IWorkflowInfo(self.context)
            info.fireTransition(self.transition.transition_id, comment=comments.get('body'))
            self._done = True
            self.request.response.redirect(self._next)

    def nextURL(self):
        return '%s/@@properties.html' % absoluteURL(self.context, self.request)

    def render(self):
        if self._done and (self.request.response.getStatus() in (302, 303)): # redirect
            return ''
        return super(WorkflowBaseForm, self).render()


class WorkflowPublishForm(WorkflowBaseForm):
    """Workflow publish form"""

    fields = field.Fields(IWorkflowContentInfo).select('publication_effective_date', 'publication_expiration_date')


class IWorkflowDeleteFormButtons(Interface):
    submit = jsaction.JSButton(title=_("Submit"))


class WorkflowDeleteForm(ajax.AJAXRequestHandler, WorkflowBaseForm):
    """Workflow delete form"""

    buttons = button.Buttons(IWorkflowDeleteFormButtons)

    def update(self):
        super(WorkflowDeleteForm, self).update()
        ztfy_blog_back.need()

    @jsaction.handler(buttons['submit'])
    def submit_handler(self, event, selector):
        return '$.ZBlog.topic.remove(this.form);'

    def nextURL(self):
        return '%s/@@topics.html' % absoluteURL(getParent(self.context, ITopicContainer), self.request)

    @ajax.handler
    def ajaxDelete(self):
        target = self.nextURL()
        info = IWorkflowInfo(self.context)
        info.fireTransition(self.transition.transition_id)
        writer = getUtility(IJSONWriter)
        return writer.write({ 'url': target })
