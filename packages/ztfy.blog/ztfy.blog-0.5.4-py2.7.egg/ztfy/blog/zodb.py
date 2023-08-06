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
from BTrees.OOBTree import OOBTree
from persistent.list import PersistentList

# import Zope3 interfaces
from zodbbrowser.interfaces import IObjectHistory

# import local interfaces

# import Zope3 packages
from zodbbrowser.state import GenericState
from zope.component import adapts

# import local packages
from ztfy.blog.ordered import OrderedContainer


class OrderedContainerState(GenericState):
    """Convenient access to an OrderedContainer's items"""

    adapts(OrderedContainer, dict, None)

    def listItems(self):
        # Now this is tricky: we want to construct a small object graph using
        # old state pickles without ever calling __setstate__ on a real
        # Persistent object, as _that_ would poison ZODB in-memory caches
        # in a nasty way (LP #487243).
        container = OrderedContainer()
        container.__setstate__(self.state)
        old_data_state = IObjectHistory(container._data).loadState(self.tid)
        old_order_state = IObjectHistory(container._order).loadState(self.tid)
        container._data = OOBTree()
        container._data.__setstate__(old_data_state)
        container._order = PersistentList()
        container._order.__setstate__(old_order_state)
        return container.items()
