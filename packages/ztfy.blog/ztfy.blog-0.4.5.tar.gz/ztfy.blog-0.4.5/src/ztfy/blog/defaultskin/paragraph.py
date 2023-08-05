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
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

# import Zope3 interfaces
from z3c.template.interfaces import IContentTemplate

# import local interfaces
from ztfy.blog.browser.interfaces.paragraph import IParagraphRenderer
from ztfy.blog.defaultskin.layer import IZBlogDefaultLayer
from ztfy.blog.paragraphs.interfaces import ITextParagraph, ICodeParagraph, IHTMLParagraph, IIllustration, \
                                            POSITION_LEFT, POSITION_RIGHT
from ztfy.file.interfaces import IImageDisplay

# import Zope3 packages
from z3c.language.switch.interfaces import II18n
from zope.component import adapts, queryMultiAdapter
from zope.interface import implements
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.blog.browser.interfaces.skin import ITopicIndexView
from ztfy.jqueryui import jquery_fancybox


class ParagraphRenderer(object):
    """Text paragraph renderer"""

    def __init__(self, context, view, request):
        self.context = context
        self.view = view
        self.request = request

    def update(self):
        pass

    def render(self):
        template = queryMultiAdapter((self, self.request), IContentTemplate)
        return template(self)


class TextParagraphRenderer(ParagraphRenderer):
    """Text paragraph renderer"""

    adapts(ITextParagraph, ITopicIndexView, IZBlogDefaultLayer)
    implements(IParagraphRenderer)


class CodeParagraphRenderer(ParagraphRenderer):
    """Code paragraph renderer"""

    adapts(ICodeParagraph, ITopicIndexView, IZBlogDefaultLayer)
    implements(IParagraphRenderer)


class CodeParagraphView(object):

    def __call__(self):
        lexer = get_lexer_by_name(self.context.body_lexer)
        formatter = HtmlFormatter(style=self.context.body_style, full=True, linenos='table')
        return highlight(self.context.body, lexer, formatter).replace('<h2></h2>', '')


class HTMLParagraphRenderer(ParagraphRenderer):
    """HTML paragraph renderer"""

    adapts(IHTMLParagraph, ITopicIndexView, IZBlogDefaultLayer)
    implements(IParagraphRenderer)


class IllustrationRenderer(ParagraphRenderer):
    """Illustration renderer"""

    adapts(IIllustration, ITopicIndexView, IZBlogDefaultLayer)
    implements(IParagraphRenderer)

    def update(self):
        if self.context.zoomable:
            jquery_fancybox.need()

    @property
    def css_class(self):
        result = 'illustration'
        position = self.context.position
        if position == POSITION_LEFT:
            result += ' toleft'
        elif position == POSITION_RIGHT:
            result += ' toright'
        return result

    @property
    def img_src(self):
        img = II18n(self.context).queryAttribute('body', request=self.request)
        if self.context.display_width:
            display = IImageDisplay(img).getDisplay('w%d' % self.context.display_width)
            url = absoluteURL(display, request=self.request)
        else:
            url = absoluteURL(img, request=self.request)
        return url

    @property
    def zoom_target(self):
        img = II18n(self.context).queryAttribute('body', request=self.request)
        if self.context.zoom_width:
            display = IImageDisplay(img).getDisplay('w%d' % self.context.zoom_width)
            url = absoluteURL(display, request=self.request)
        else:
            url = absoluteURL(img, request=self.request)
        return url
