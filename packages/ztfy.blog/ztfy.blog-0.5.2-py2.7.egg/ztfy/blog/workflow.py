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
import pytz
from datetime import datetime

# import Zope3 interfaces
from zope.dublincore.interfaces import IZopeDublinCore

# import local interfaces
from ztfy.blog.interfaces import STATUS_DRAFT, STATUS_PUBLISHED, STATUS_RETIRED, STATUS_ARCHIVED, STATUS_DELETED
from ztfy.blog.interfaces import STATUS_VOCABULARY
from ztfy.workflow.interfaces import IWorkflowContent

# import Zope3 packages
from zope.traversing.api import getName, getParent

# import local packages
from hurry.workflow.workflow import Transition
from ztfy.security.security import getSecurityManager
from ztfy.utils.request import getRequest
from ztfy.workflow.workflow import Workflow

from ztfy.blog import _


def canPublish(wf, context):
    sm = getSecurityManager(context)
    if sm is None:
        request = getRequest()
        dc = IZopeDublinCore(context)
        return request.principal.id == dc.creators[0]
    return sm.canUsePermission('ztfy.ManageContent') or sm.canUsePermission('ztfy.ManageBlog')

def publishAction(wf, context):
    """Publihs draft content"""
    now = datetime.now(pytz.UTC)
    wf_content = IWorkflowContent(context)
    if wf_content.first_publication_date is None:
        wf_content.first_publication_date = now
    IWorkflowContent(context).publication_date = now


def canRetire(wf, context):
    sm = getSecurityManager(context)
    if sm is None:
        request = getRequest()
        dc = IZopeDublinCore(context)
        return request.principal.id == dc.creators[0]
    return sm.canUsePermission('ztfy.ManageContent') or sm.canUsePermission('ztfy.ManageBlog')

def retireAction(wf, context):
    """Archive published content"""
    now = datetime.now(pytz.UTC)
    IWorkflowContent(context).publication_expiration_date = now


def canArchive(wf, context):
    sm = getSecurityManager(context)
    if sm is None:
        request = getRequest()
        dc = IZopeDublinCore(context)
        return request.principal.id == dc.creators[0]
    return sm.canUsePermission('ztfy.ManageContent') or sm.canUsePermission('ztfy.ManageBlog')

def archiveAction(wf, context):
    """Archive published content"""
    now = datetime.now(pytz.UTC)
    content = IWorkflowContent(context)
    content.publication_expiration_date = min(content.publication_expiration_date or now, now)


def canDelete(wf, context):
    sm = getSecurityManager(context)
    if sm is None:
        request = getRequest()
        dc = IZopeDublinCore(context)
        return request.principal.id == dc.creators[0]
    return sm.canUsePermission('ztfy.ManageContent') or sm.canUsePermission('ztfy.ManageBlog')

def deleteAction(wf, context):
    """Delete draft version"""
    parent = getParent(context)
    name = getName(context)
    del parent[name]


init = Transition('init',
                  title=_("Initialize"),
                  source=None,
                  destination=STATUS_DRAFT,
                  order=0)

draft_to_published = Transition('draft_to_published',
                                title=_("Publish"),
                                source=STATUS_DRAFT,
                                destination=STATUS_PUBLISHED,
                                condition=canPublish,
                                action=publishAction,
                                order=1,
                                view='wf_publish.html',
                                html_help=_('''This content is currently in DRAFT mode.
                                               Publishing it will make it publicly visible.'''))

published_to_retired = Transition('published_to_retired',
                                  title=_("Retire"),
                                  source=STATUS_PUBLISHED,
                                  destination=STATUS_RETIRED,
                                  condition=canRetire,
                                  action=retireAction,
                                  order=2,
                                  view='wf_default.html',
                                  html_help=_('''This content is actually published.
                                                 You can retire it to make it unvisible.'''))

retired_to_published = Transition('retired_to_published',
                                  title=_("Re-publish"),
                                  source=STATUS_RETIRED,
                                  destination=STATUS_PUBLISHED,
                                  condition=canPublish,
                                  action=publishAction,
                                  order=3,
                                  view='wf_publish.html',
                                  html_help=_('''This content was published and retired after.
                                                 You can re-publish it to make it visible again.'''))

published_to_archived = Transition('published_to_archived',
                                   title=_("Archive"),
                                   source=STATUS_PUBLISHED,
                                   destination=STATUS_ARCHIVED,
                                   condition=canArchive,
                                   action=archiveAction,
                                   order=4,
                                   view='wf_default.html',
                                   html_help=_('''This content is currently published.
                                                  If it is archived, it will not be possible to make it visible again !'''))

retired_to_archived = Transition('retired_to_archived',
                                 title=_("Archive"),
                                 source=STATUS_RETIRED,
                                 destination=STATUS_ARCHIVED,
                                 condition=canArchive,
                                 action=archiveAction,
                                 order=5,
                                 view='wf_default.html',
                                 html_help=_('''This content has been published but is currently retired.
                                                If it is archived, it will not be possible to make it visible again !'''))

deleted = Transition('delete',
                     title=_("Delete"),
                     source=STATUS_DRAFT,
                     destination=STATUS_DELETED,
                     condition=canDelete,
                     action=deleteAction,
                     order=6,
                     view='wf_delete.html',
                     html_help=_('''This content has never been published.
                                    It can be removed and definitely deleted.'''))

wf_transitions = [init,
                  draft_to_published,
                  published_to_retired,
                  retired_to_published,
                  published_to_archived,
                  retired_to_archived,
                  deleted]
wf = Workflow(wf_transitions,
              states=STATUS_VOCABULARY,
              published_states=(STATUS_PUBLISHED,))
