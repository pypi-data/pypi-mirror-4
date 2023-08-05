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
from zope.schema.interfaces import IVocabularyFactory

# import local interfaces

# import Zope3 packages
from z3c.template.template import getViewTemplate
from zope.component import getUtility
from zope.i18n import translate
from zope.publisher.browser import BrowserView
from zope.traversing.api import getName

# import local packages

from ztfy.blog import _


class ResourceView(BrowserView):
    """Resource view"""

    __call__ = getViewTemplate()

    @property
    def title(self):
        return II18n(self.context).queryAttribute('title', request=self.request) or \
               self.context.filename or \
               getName(self.context)

    @property
    def language(self):
        lang = self.context.language
        if not lang:
            return None
        vocabulary = getUtility(IVocabularyFactory, 'ZTFY languages')
        return translate(_("Language: %s") % vocabulary(self.context).getTerm(lang).title, context=self.request)

    @property
    def flag(self):
        lang = self.context.language
        if not lang:
            return None
        return lang.replace('-', '_', 1)
