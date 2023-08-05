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
from pygments import lexers, styles

# import Zope3 interfaces

# import local interfaces
from ztfy.blog.interfaces.paragraph import IParagraphInfo, IParagraphWriter, IParagraph

# import Zope3 packages
from zope.schema import Choice, Bool, Int, Text
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

# import local packages
from ztfy.i18n.schema import I18nText, I18nHTML, I18nImage

from ztfy.blog import _


# Text paragraphs

class ITextParagraphInfo(IParagraphInfo):
    """Text paragraph base interface"""

    body = I18nText(title=_("Body"),
                    description=_("Main paragraph's content"),
                    required=False)

    body_format = Choice(title=_("Body text format"),
                         description=_("Text format of paragraph's body"),
                         required=True,
                         default=u'zope.source.plaintext',
                         vocabulary='SourceTypes')


class ITextParagraphWriter(IParagraphWriter):
    """Text paragraph writer interface"""


class ITextParagraph(IParagraph, ITextParagraphInfo, ITextParagraphWriter):
    """Text paragraph full interface"""


# Code paragraphs

_lexers_by_name = {}
_lexers_by_alias = {}
for name, aliases, _i1, _i2 in lexers.get_all_lexers():
    alias = aliases[0]
    if (not _lexers_by_name.get(name)) and (not _lexers_by_alias.get(alias)):
        _lexers_by_name[name] = alias
        _lexers_by_alias[alias] = name

PYGMENTS_LEXERS_VOCABULARY = SimpleVocabulary([SimpleTerm(i, t, t) for t, i in sorted(_lexers_by_name.items())])

PYGMENTS_STYLES_VOCABULARY = SimpleVocabulary([SimpleTerm(i, i, i) for i in sorted(styles.get_all_styles())])


class ICodeParagraphInfo(IParagraphInfo):
    """Code paragraph base interface"""

    body = Text(title=_("Body"),
                description=_("Main paragraph's content"),
                required=False)

    body_lexer = Choice(title=_("Body source language"),
                        description=_("Original language of the body code"),
                        required=True,
                        default=u'python',
                        vocabulary=PYGMENTS_LEXERS_VOCABULARY)

    body_style = Choice(title=_("Body style"),
                        description=_("Color style of code body"),
                        required=True,
                        default=u'default',
                        vocabulary=PYGMENTS_STYLES_VOCABULARY)


class ICodeParagraphWriter(IParagraphWriter):
    """Code paragraph writer interface"""


class ICodeParagraph(IParagraph, ICodeParagraphInfo, ICodeParagraphWriter):
    """Code paragraph full interface"""


# HTML paragraphs

class IHTMLParagraphInfo(IParagraphInfo):
    """HTML paragraph base interface"""

    body = I18nHTML(title=_("Body"),
                    description=_("Main paragraph's content"),
                    required=False)


class IHTMLParagraphWriter(IParagraphWriter):
    """HTML paragraph writer interface"""


class IHTMLParagraph(IParagraph, IHTMLParagraphInfo, IHTMLParagraphWriter):
    """HTML paragraph full interface"""


# Illustrations

POSITION_LEFT = 0
POSITION_RIGHT = 1
POSITION_CENTER = 2

POSITION_IDS = [ 'left', 'right', 'center' ]
POSITION_LABELS = (_("Floating left to next paragraph"),
                   _("Floating right to next paragraph"),
                   _("Centered before next paragraph"))

POSITION_VOCABULARY = SimpleVocabulary([SimpleTerm(i, i, t) for i, t in enumerate(POSITION_LABELS)])


class IIllustrationInfo(IParagraphInfo):
    """Illustration base interface"""

    body = I18nImage(title=_("Illustration content"),
                     description=_("Image file containing illustration"),
                     required=True)

    position = Choice(title=_("Illustration's position"),
                      description=_("Position of the displayed illustration"),
                      required=True,
                      vocabulary=POSITION_VOCABULARY)

    display_width = Int(title=_("Display width"),
                        description=_("Width of the displayed illustration"),
                        required=False)

    break_after = Bool(title=_("Linebreak after illustration ?"),
                       description=_("If 'Yes', a linebreak will be inserted after illustration"),
                       required=True,
                       default=False)

    zoomable = Bool(title=_("Zoomable ?"),
                    description=_("If a display width is applied, can the illustration be zoomed ?"),
                    required=True,
                    default=False)

    zoom_width = Int(title=_("Zoom width"),
                     description=_("Width of the illustration displayed in zoom mode"),
                     required=False)


class IIllustrationWriter(IParagraphWriter):
    """Illustration writer interface"""


class IIllustration(IParagraph, IIllustrationInfo, IIllustrationWriter):
    """Illustration full interface"""
