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
from ztfy.blog.paragraphs.interfaces import ICodeParagraph

# import Zope3 packages
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.blog.paragraph import Paragraph


class CodeParagraph(Paragraph):

    implements(ICodeParagraph)

    body = FieldProperty(ICodeParagraph['body'])
    body_lexer = FieldProperty(ICodeParagraph['body_lexer'])
    body_style = FieldProperty(ICodeParagraph['body_style'])
