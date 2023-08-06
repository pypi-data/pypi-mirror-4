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
from persistent import Persistent

# import Zope3 interfaces
from zope.annotation.interfaces import IAnnotations

# import local interfaces
from ztfy.blog.interfaces.google import IGoogleAnalytics, IGoogleAdSense, TOP, TOP_TOPICS, BOTTOM, BOTTOM_TOPICS
from ztfy.blog.interfaces.site import ISiteManager
from ztfy.blog.interfaces.topic import ITopic

# import Zope3 packages
from zope.component import adapter
from zope.interface import implementer, implements
from zope.schema.fieldproperty import FieldProperty

# import local packages


class GoogleAnalytics(Persistent):
    """Google Analytics persistent class"""

    implements(IGoogleAnalytics)

    enabled = FieldProperty(IGoogleAnalytics['enabled'])
    website_id = FieldProperty(IGoogleAnalytics['website_id'])
    verification_code = FieldProperty(IGoogleAnalytics['verification_code'])


ANALYTICS_ANNOTATIONS_KEY = 'ztfy.blog.google.analytics'

@adapter(ISiteManager)
@implementer(IGoogleAnalytics)
def GoogleAnalyticsFactory(context):
    """Google Analytics adapter factory"""
    annotations = IAnnotations(context)
    adapter = annotations.get(ANALYTICS_ANNOTATIONS_KEY)
    if adapter is None:
        adapter = annotations[ANALYTICS_ANNOTATIONS_KEY] = GoogleAnalytics()
    return adapter


class GoogleAdSense(Persistent):
    """Google AdSense persistent class"""

    implements(IGoogleAdSense)

    enabled = FieldProperty(IGoogleAdSense['enabled'])
    client_id = FieldProperty(IGoogleAdSense['client_id'])
    slot_id = FieldProperty(IGoogleAdSense['slot_id'])
    slot_width = FieldProperty(IGoogleAdSense['slot_width'])
    slot_height = FieldProperty(IGoogleAdSense['slot_height'])
    slot_position = FieldProperty(IGoogleAdSense['slot_position'])

    def display(self, context, position):
        if not self.enabled:
            return False
        if ((position == 'top') and (self.slot_position in (BOTTOM, BOTTOM_TOPICS))) or \
           ((position == 'bottom') and (self.slot_position in (TOP, TOP_TOPICS))):
            return False
        return ITopic.providedBy(context) or (self.slot_position in (TOP, BOTTOM))


ADSENSE_ANNOTATIONS_KEY = 'ztfy.blog.google.adsense'

@adapter(ISiteManager)
@implementer(IGoogleAdSense)
def GoogleAdSenseFactory(context):
    """Google AdSense adapter"""
    annotations = IAnnotations(context)
    adapter = annotations.get(ADSENSE_ANNOTATIONS_KEY)
    if adapter is None:
        adapter = annotations[ADSENSE_ANNOTATIONS_KEY] = GoogleAdSense()
    return adapter
