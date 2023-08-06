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

# import local interfaces

# import Zope3 packages
from zope.interface import Interface
from zope.schema import Text

# import local packages

from ztfy.blog import _


class IIdColumn(Interface):
    """Marker interface for ID column"""


class INameColumn(Interface):
    """Marker interface for name column"""


class ITitleColumn(Interface):
    """Marker interface for title column"""


class IStatusColumn(Interface):
    """Marker interface for status column"""


class IActionsColumn(Interface):
    """Marker interface for actions column"""


class IContainerTableViewTitleCell(Interface):
    """Container table view title cell adapter"""

    prefix = Text(title=_("Text displayed before title link"))

    before = Text(title=_("Text displayed before cell main text"))

    after = Text(title=_("Text displayed after cell main text"))

    suffix = Text(title=_("Text displayed after title link"))


class IContainerTableViewStatusCell(Interface):
    """Container table view status cell interface"""

    content = Text(title=_("Content of status cell"))


class IContainerTableViewActionsCell(Interface):
    """Container table view actions cell interface"""

    content = Text(title=_("Content of actions cell"))
