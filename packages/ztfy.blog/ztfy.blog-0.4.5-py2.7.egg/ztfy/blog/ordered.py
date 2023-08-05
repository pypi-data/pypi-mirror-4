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

# import local interfaces
from ztfy.skin.interfaces import IOrderedContainer

# import Zope3 packages
from zope.container.ordered import OrderedContainer as OrderedContainerBase
from zope.interface import implements
from zope.traversing.api import getName

# import local packages


class OrderedContainer(OrderedContainerBase):

    implements(IOrderedContainer)

    def __init__(self):
        self._data = OOBTree()
        self._order = PersistentList()

    def updateOrder(self, order, iface=None):
        if iface is not None:
            order = [id for id in order if iface.providedBy(self[id])] + \
                    [getName(i) for i in self.values() if not iface.providedBy(i)]
        else:
            order = order + [k for k in self.keys() if k not in order]
        super(OrderedContainer, self).updateOrder(order)

    def moveUp(self, id):
        keys = list(self.keys())
        index = keys.index(id)
        if index > 0:
            keys[index - 1], keys[index] = keys[index], keys[index - 1]
            self.context.updateOrder(keys)

    def moveDown(self, id):
        keys = list(self.keys())
        index = keys.index(id)
        if index < len(keys) - 1:
            keys[index + 1], keys[index] = keys[index], keys[index + 1]
            self.context.updateOrder(keys)

    def moveFirst(self, id):
        keys = list(self.keys())
        index = keys.index(id)
        if index > 0:
            keys = keys[index:index + 1] + keys[:index] + keys[index + 1:]
            self.updateOrder(keys)

    def moveLast(self, id):
        keys = list(self.keys())
        index = keys.index(id)
        if index < len(keys) - 1:
            keys = keys[:index] + keys[index + 1:] + keys[index:index + 1]
            self.context.updateOrder(keys)
