### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2011 Thierry Florac <tflorac AT ulthar.net>
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
from fanstatic import Library, Resource

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages
from ztfy.blog.browser import ztfy_blog_front
from ztfy.skin import ztfy_skin


library = Library('ztfy.blog.defaultskin', 'resources')

ztfy_blog_defaultskin_css = Resource(library, 'css/defaultskin.css', minified='css/defaultskin.min.css',
                                     depends=[ztfy_skin])
ztfy_blog_defaultskin = Resource(library, 'js/defaultskin.js', minified='js/defaultskin.min.js',
                                 depends=[ztfy_blog_front, ztfy_blog_defaultskin_css])
