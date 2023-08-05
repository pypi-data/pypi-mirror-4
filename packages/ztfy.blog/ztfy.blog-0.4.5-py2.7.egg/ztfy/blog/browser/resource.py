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
from cStringIO import StringIO
import tarfile
import zipfile

# import Zope3 interfaces
from z3c.language.switch.interfaces import II18n
from zope.app.file.interfaces import IFile, IImage
from zope.dublincore.interfaces import IZopeDublinCore
from zope.intid.interfaces import IIntIds
from zope.traversing.interfaces import TraversalError

# import local interfaces
from ztfy.blog.browser.interfaces.container import IActionsColumn
from ztfy.blog.browser.interfaces.container import IContainerTableViewActionsCell
from ztfy.blog.interfaces.resource import IResource, IResourceInfo, IResourceContainer, IResourceContainerTarget
from ztfy.file.interfaces import IImageDisplay
from ztfy.skin.layer import IZTFYBrowserLayer, IZTFYBackLayer

# import Zope3 packages
from z3c.form import field
from z3c.formjs import ajax
from z3c.table.column import Column
from z3c.template.template import getLayoutTemplate
from zope.component import adapts, getUtility, queryMultiAdapter
from zope.event import notify
from zope.i18n import translate
from zope.interface import implements, Interface
from zope.lifecycleevent import ObjectCreatedEvent
from zope.publisher.browser import BrowserPage, BrowserView
from zope.traversing import namespace
from zope.traversing.api import getParent as getParentAPI, getName
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.blog.browser.content import BaseContentDefaultBackViewAdapter
from ztfy.blog.resource import Resource
from ztfy.file.schema import FileField
from ztfy.i18n.browser import ztfy_i18n
from ztfy.skin.container import OrderedContainerBaseView
from ztfy.skin.form import DialogAddForm, DialogEditForm
from ztfy.skin.menu import MenuItem, JsMenuItem
from ztfy.utils.traversing import getParent
from ztfy.utils.unicode import translateString

from ztfy.blog import _


class ResourceDefaultViewAdapter(BaseContentDefaultBackViewAdapter):

    adapts(IResource, IZTFYBackLayer, Interface)

    def getAbsoluteURL(self):
        return '''javascript:$.ZTFY.dialog.open('%s/%s')''' % (absoluteURL(self.context, self.request), self.viewname)


class ResourceContainerNamespaceTraverser(namespace.view):
    """++static++ namespace"""

    def traverse(self, name, ignored):
        result = getParent(self.context, IResourceContainerTarget)
        if result is not None:
            return IResourceContainer(result)
        raise TraversalError('++static++')


class IResourceAddFormMenuTarget(Interface):
    """Marker interface for resource add menu"""


class ResourceContainerContentsViewMenuItem(MenuItem):
    """Resources container contents menu"""

    title = _("Resources")


class IResourceContainerContentsView(Interface):
    """Marker interface for resource container contents view"""

class ResourceContainerContentsView(OrderedContainerBaseView):
    """Resources container contents view"""

    implements(IResourceAddFormMenuTarget, IResourceContainerContentsView)

    legend = _("Topic resources")
    cssClasses = { 'table': 'orderable' }

    @property
    def values(self):
        return IResourceContainer(self.context).values()

    @ajax.handler
    def ajaxRemove(self):
        oid = self.request.form.get('id')
        if oid:
            intids = getUtility(IIntIds)
            target = intids.getObject(int(oid))
            parent = getParentAPI(target)
            del parent[getName(target)]
            return "OK"
        return "NOK"

    @ajax.handler
    def ajaxUpdateOrder(self):
        self.updateOrder(IResourceContainer(self.context))


class IResourceContainerPreviewColumn(Interface):
    """Marker interface for resource container preview column"""

class ResourceContainerPreviewColumn(Column):
    """Resource container preview column"""

    implements(IResourceContainerPreviewColumn)

    header = u''
    weight = 5
    cssClasses = { 'th': 'preview',
                   'td': 'preview' }

    def renderCell(self, item):
        image = IImage(item.content, None)
        if image is None:
            return u''
        i18n = II18n(image, None)
        if i18n is None:
            alt = IZopeDublinCore(image).title
        else:
            alt = II18n(image).queryAttribute('title', request=self.request)
        display = IImageDisplay(image).getDisplay('64x64')
        return '''<img src="%s" alt="%s" />''' % (absoluteURL(display, self.request), alt)


class IResourceContainerSizeColumn(Interface):
    """Marker interface for resource container size column"""

class ResourceContainerSizeColumn(Column):
    """Resource container size column"""

    implements(IResourceContainerSizeColumn)

    header = _("Size")
    weight = 15
    cssClasses = { 'td': 'size' }

    def __init__(self, context, request, table):
        super(ResourceContainerSizeColumn, self).__init__(context, request, table)
        self.formatter = self.request.locale.numbers.getFormatter('decimal')

    def renderCell(self, item):
        file = IFile(item.content, None)
        if file is None:
            return u''
        size = file.getSize()
        if size < 1024:
            return translate(_("%d bytes"), context=self.request) % size
        size = size / 1024.0
        if size < 1024:
            return translate(_("%s Kb"), context=self.request) % self.formatter.format(size, '0.00')
        size = size / 1024.0
        return translate(_("%s Mb"), context=self.request) % self.formatter.format(size, '0.00')


class ResourceContainerContentsViewActionsColumnCellAdapter(object):

    adapts(IResource, IZTFYBrowserLayer, IResourceContainerContentsView, IActionsColumn)
    implements(IContainerTableViewActionsCell)

    def __init__(self, context, request, view, column):
        self.context = context
        self.request = request
        self.view = view
        self.column = column
        self.intids = getUtility(IIntIds)

    @property
    def content(self):
        klass = "ui-workflow ui-icon ui-icon-trash"
        result = '''<span class="%s" title="%s" onclick="$.ZTFY.form.remove(%d, this);"></span>''' % (klass,
                                                                                                      translate(_("Delete resource"), context=self.request),
                                                                                                      self.intids.register(self.context))
        return result


class ResourceContainerResourcesList(BrowserView):
    """Get list of images resources used by HTML editor"""

    def getImagesList(self):
        self.request.response.setHeader('Content-Type', 'text/javascript')
        resources = IResourceContainer(self.context).values()
        images = [img for img in resources if img.content.contentType.startswith('image/')]
        return '''var tinyMCEImageList = new Array(
            %s
        );''' % ',\n'.join(['["%s","%s"]' % (II18n(img).queryAttribute('title', request=self.request) or ('{{ %s }}' % getName(img)),
                                             absoluteURL(img, self.request)) for img in images])

    def getLinksList(self):
        self.request.response.setHeader('Content-Type', 'text/javascript')
        resources = IResourceContainer(self.context).values()
        return '''var tinyMCELinkList = new Array(
            %s
        );''' % ',\n'.join(['["%s","%s"]' % (II18n(res).queryAttribute('title', request=self.request) or ('{{ %s }}' % getName(res)),
                                             absoluteURL(res, self.request)) for res in resources])


class ResourceContainerAddResourceMenuItem(JsMenuItem):
    """Resource add menu"""

    title = _(":: Add resource...")

    def render(self):
        ztfy_i18n.need()
        return super(ResourceContainerAddResourceMenuItem, self).render()


class ResourceAddForm(DialogAddForm):
    """Resource add form"""

    title = _("New resource")
    legend = _("Adding new resource")

    fields = field.Fields(IResourceInfo)
    layout = getLayoutTemplate()
    parent_interface = IResourceContainerTarget
    parent_view = ResourceContainerContentsView
    handle_upload = True

    def create(self, data):
        return Resource()

    def add(self, resource):
        filename = self.request.form.get('form.widgets.filename')
        if filename:
            filename = translateString(filename, escapeSlashes=True, forceLower=False, spaces='-')
        else:
            filename = translateString(self.request.form.get('form.widgets.content').filename, escapeSlashes=True, forceLower=True, spaces='-')
        self.context[filename] = resource


class ResourceContainerAddResourcesFromZipMenuItem(JsMenuItem):
    """Resources from ZIP add menu"""

    title = _(":: Add resources from archive...")

    def render(self):
        ztfy_i18n.need()
        return super(ResourceContainerAddResourcesFromZipMenuItem, self).render()


class IZipResourceAddInfo(Interface):
    """ZipResourceAddForm schema"""

    content = FileField(title=_("Archive data"),
                        description=_("Archive content's will be extracted as resources ; format can be any ZIP, tar.gz or tar.bz2 file"),
                        required=True)


class ZipArchiveExtractor(object):

    def __init__(self, data):
        self.data = zipfile.ZipFile(StringIO(data), 'r')

    def getMembers(self):
        return self.data.infolist()

    def getFilename(self, member):
        return member.filename

    def extract(self, member):
        return self.data.read(member.filename)


class TarArchiveExtractor(object):

    def __init__(self, data):
        self.data = tarfile.open(fileobj=StringIO(data), mode='r')

    def getMembers(self):
        return self.data.getmembers()

    def getFilename(self, member):
        return member.name

    def extract(self, member):
        output = self.data.extractfile(member)
        if output is not None:
            return output.read()
        return None


class ResourcesFromZipAddForm(DialogAddForm):
    """Add a set of resources included in a ZIP archive file"""

    title = _("New resources")
    legend = _("Adding new resources from ZIP file")

    fields = field.Fields(IZipResourceAddInfo)
    layout = getLayoutTemplate()
    parent_interface = IResourceContainerTarget
    parent_view = ResourceContainerContentsView
    handle_upload = True

    def createAndAdd(self, data):
        filename = self.request.form.get('form.widgets.content').filename
        if filename.lower().endswith('.zip'):
            extractor = ZipArchiveExtractor
        else:
            extractor = TarArchiveExtractor
        content = data.get('content')
        if isinstance(content, tuple):
            content = content[0]
        extractor = extractor(content)
        for info in extractor.getMembers():
            content = extractor.extract(info)
            if content:
                name = translateString(extractor.getFilename(info), escapeSlashes=True, forceLower=False, spaces='-')
                resource = Resource()
                notify(ObjectCreatedEvent(resource))
                self.context[name] = resource
                resource.filename = name
                resource.content = content


class ResourceEditForm(DialogEditForm):
    """Resource edit form"""

    legend = _("Edit resource properties")

    fields = field.Fields(IResourceInfo)
    layout = getLayoutTemplate()
    parent_interface = IResourceContainerTarget
    parent_view = ResourceContainerContentsView
    handle_upload = True


class ResourceIndexView(BrowserPage):
    """Resource default view"""

    def __call__(self):
        view = queryMultiAdapter((self.context.content, self.request), Interface, 'index.html')
        return view()
