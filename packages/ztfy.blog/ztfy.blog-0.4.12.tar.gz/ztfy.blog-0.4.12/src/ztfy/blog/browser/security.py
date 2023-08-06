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
from zope.authentication.interfaces import IAuthentication

# import local interfaces

# import Zope3 packages
from z3c.formjs import ajax
from z3c.json.interfaces import IJSONWriter
from zope.component import getUtility

# import local packages


class LoginLogoutView(ajax.AJAXRequestHandler):
    """Base login/logout view"""

    @ajax.handler
    def login(self):
        auth = getUtility(IAuthentication)
        writer = getUtility(IJSONWriter)
        if auth.authenticate(self.request) is not None:
            return writer.write('OK')
        return writer.write('NOK')

    @ajax.handler
    def logout(self):
        auth = getUtility(IAuthentication)
        writer = getUtility(IJSONWriter)
        if auth.logout(self.request):
            return writer.write('OK')
        return writer.write('NOK')
