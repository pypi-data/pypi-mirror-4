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

# import local packages


class ISkinTalesAPI(Interface):
    """'skin:' TALES namespace interface"""

    def presentation():
        """Get presentation of adapted context"""


class ISiteManagerTalesAPI(Interface):
    """'site:' TALES namespace interface"""

    def manager():
        """Get site manager parent of given context"""

    def presentation():
        """Get site manager presentation of given context"""


class IGoogleTalesAPI(Interface):
    """'google' TALES namespace interface"""

    def analytics():
        """Get site manager Google Analytics adapter"""

    def adsense():
        """Get site manager Google AdSense adapter"""


class IContentMetasAPI(Interface):
    """'metas' TALES namespace interface"""

    def items():
        """Get list of metas headers"""

    def render():
        """Get content metas headers"""
