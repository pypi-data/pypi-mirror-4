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
from ztfy.blog.paragraphs.interfaces import IIllustration

# import local interfaces
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

# import Zope3 packages
from ztfy.blog.paragraph import Paragraph
from ztfy.extfile.blob import BlobImage
from ztfy.i18n.property import I18nImageProperty

# import local packages


class Illustration(Paragraph):

    implements(IIllustration)

    body = I18nImageProperty(IIllustration['body'], klass=BlobImage, img_klass=BlobImage)
    position = FieldProperty(IIllustration['position'])
    display_width = FieldProperty(IIllustration['display_width'])
    break_after = FieldProperty(IIllustration['break_after'])
    zoomable = FieldProperty(IIllustration['zoomable'])
    zoom_width = FieldProperty(IIllustration['zoom_width'])
