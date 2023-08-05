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
from zope.container.interfaces import IContainer

# import local interfaces
from ztfy.blog.interfaces import IBaseContent
from ztfy.blog.interfaces.category import ICategoriesTarget
from ztfy.blog.interfaces.link import ILinkContainerTarget
from ztfy.blog.interfaces.paragraph import IParagraphContainer
from ztfy.blog.interfaces.resource import IResourceContainerTarget
from ztfy.workflow.interfaces import IWorkflowTarget

# import Zope3 packages
from zope.container.constraints import containers, contains
from zope.interface import Interface
from zope.schema import Int, Bool, List, Object

# import local packages

from ztfy.blog import _


#
# Topics management
#

class ITopicInfo(IBaseContent):
    """Base topic interface"""

    publication_year = Int(title=_("Publication year"),
                           description=_("Topic publication year, used for indexing"),
                           readonly=True)

    publication_month = Int(title=_("Publication month"),
                            description=_("Topic publication month, used for indexing"),
                            readonly=True)

    commentable = Bool(title=_("Allow comments ?"),
                       description=_("Are free comments allowed on this topic ?"),
                       required=True,
                       default=True)


class ITopicWriter(Interface):
    """Topic writer interface"""


class ITopic(ITopicInfo, ITopicWriter, IParagraphContainer, IWorkflowTarget,
             ICategoriesTarget, IResourceContainerTarget, ILinkContainerTarget):
    """Topic full interface"""

    containers('ztfy.blog.interfaces.topic.ITopicContainer')
    contains('ztfy.blog.interfaces.ITopicElement')


class ITopicContainerInfo(Interface):
    """Topic container interface"""

    topics = List(title=_("Topics list"),
                  value_type=Object(schema=ITopic),
                  readonly=True)

    def getVisibleTopics(request):
        """Get list of topics visible from given request"""


class ITopicContainerWriter(Interface):
    """Topic container writer interface"""

    def addTopic(topic):
        """Add new topic to container"""


class ITopicContainer(IContainer, ITopicContainerInfo, ITopicContainerWriter):
    """Topic container interface"""
