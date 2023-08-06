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
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.schema.interfaces import IVocabularyFactory

# import local interfaces
from ztfy.blog.layer import IZTFYBlogFrontLayer

# import Zope3 packages
from zope.component import getUtilitiesFor
from zope.componentvocabulary.vocabulary import UtilityVocabulary, UtilityTerm
from zope.interface import classProvides
from zope.i18n import translate
from zope.schema import getFields

# import local packages
from ztfy.utils.request import getRequest


class SkinsVocabulary(UtilityVocabulary):

    classProvides(IVocabularyFactory)

    interface = IBrowserSkinType
    nameOnly = True

    def __init__(self, context, **kw):
        request = getRequest()
        utils = [(name, translate(getFields(util)['label'].title, context=request)) for (name, util) in getUtilitiesFor(self.interface, context)
                                                                                                     if util.extends(IZTFYBlogFrontLayer)]
        self._terms = dict((title, UtilityTerm(name, title)) for name, title in utils)


def getValues(parent, context, output):
    output.append((parent, context))
    for item in context.values():
        getValues(context, item, output)
