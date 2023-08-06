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
from zopyx.txng3.core.interfaces import IIndexableContent

# import local interfaces
from ztfy.blog.interfaces import IBaseContent

# import Zope3 packages
from zope.component import adapts
from zope.interface import implements
from zopyx.txng3.core.content import IndexContentCollector

# import local packages


class BaseContentTextIndexer(object):

    adapts(IBaseContent)
    implements(IIndexableContent)

    def __init__(self, context):
        self.context = context

    def indexableContent(self, fields):
        icc = IndexContentCollector()
        for field in fields:
            for lang, value in getattr(self.context, field, {}).items():
                if value:
                    icc.addContent(field, value, lang)
        return icc
