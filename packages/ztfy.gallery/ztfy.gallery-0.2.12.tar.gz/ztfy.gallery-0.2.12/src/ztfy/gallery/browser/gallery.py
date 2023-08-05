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
import os

# import Zope3 interfaces
from zope.intid.interfaces import IIntIds
from zope.traversing.interfaces import TraversalError

# import local interfaces
from ztfy.gallery.interfaces import IGalleryImageInfo, IGalleryImage, IGalleryImageExtension, \
                                    IGalleryContainer, IGalleryContainerTarget, IGalleryIndexManager, IGalleryIndex
from ztfy.skin.interfaces import IDefaultView
from ztfy.skin.layer import IZTFYBackLayer

# import Zope3 packages
from z3c.form import field
from z3c.formjs import ajax
from z3c.template.template import getLayoutTemplate, getViewTemplate
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import adapts, getUtility, getAdapters, queryMultiAdapter
from zope.event import notify
from zope.interface import implements, Interface
from zope.lifecycleevent import ObjectCreatedEvent
from zope.publisher.browser import BrowserView, BrowserPage
from zope.schema import TextLine
from zope.traversing import api as traversing_api
from zope.traversing import namespace
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.blog.browser.resource import ZipArchiveExtractor, TarArchiveExtractor
from ztfy.file.schema import FileField
from ztfy.gallery.browser import ztfy_gallery_back
from ztfy.gallery.gallery import GalleryImage
from ztfy.i18n.browser import ztfy_i18n
from ztfy.jqueryui import jquery_fancybox
from ztfy.skin.container import OrderedContainerBaseView
from ztfy.skin.form import DialogAddForm, DialogEditForm
from ztfy.skin.menu import MenuItem, JsMenuItem
from ztfy.utils.traversing import getParent
from ztfy.utils.unicode import translateString

from ztfy.gallery import _


class GalleryImageDefaultViewAdapter(object):

    adapts(IGalleryImage, IZTFYBackLayer, Interface)
    implements(IDefaultView)

    viewname = '@@properties.html'

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    def getAbsoluteURL(self):
        return """javascript:$.ZTFY.dialog.open('%s/%s')""" % (absoluteURL(self.context, self.request),
                                                               self.viewname)


class GalleryContainerNamespaceTraverser(namespace.view):
    """++gallery++ namespace"""

    def traverse(self, name, ignored):
        result = getParent(self.context, IGalleryContainerTarget)
        if result is not None:
            return IGalleryContainer(result)
        raise TraversalError('++gallery++')


class IGalleryImageAddFormMenuTarget(Interface):
    """Marker interface for gallery images add menu"""


class GalleryContainerContentsViewMenuItem(MenuItem):
    """Gallery container contents menu"""

    title = _("Images gallery")


class IGalleryContainerContentsView(Interface):
    """Marker interface for gallery container contents view"""

class GalleryContainerContentsView(OrderedContainerBaseView):
    """Gallery container contents view"""

    implements(IGalleryImageAddFormMenuTarget, IGalleryContainerContentsView)

    legend = _("Images gallery")
    cssClasses = { 'table': 'orderable' }

    output = ViewPageTemplateFile('templates/gallery_contents.pt')

    def update(self):
        ztfy_gallery_back.need()
        jquery_fancybox.need()
        super(GalleryContainerContentsView, self).update()

    @property
    def values(self):
        return IGalleryContainer(self.context).values()

    @property
    def hasIndex(self):
        gallery = IGalleryContainer(self.context)
        return IGalleryIndexManager.providedBy(gallery)

    @property
    def index(self):
        gallery = IGalleryContainer(self.context)
        return IGalleryIndex(gallery)

    @ajax.handler
    def ajaxRemove(self):
        oid = self.request.form.get('id')
        if oid:
            intids = getUtility(IIntIds)
            target = intids.getObject(int(oid))
            parent = traversing_api.getParent(target)
            del parent[traversing_api.getName(target)]
            return "OK"
        return "NOK"

    @ajax.handler
    def ajaxUpdateOrder(self):
        self.updateOrder(IGalleryContainer(self.context))

    def getImagesExtensions(self, image):
        return sorted((a[1] for a in getAdapters((image, self.request), IGalleryImageExtension)),
                      key=lambda x: x.weight)


class GalleryContainerAddImageMenuItem(JsMenuItem):
    """Gallery image add menu"""

    title = _(":: Add image...")

    def render(self):
        ztfy_i18n.need()
        return super(GalleryContainerAddImageMenuItem, self).render()


class GalleryImageAddForm(DialogAddForm):
    """Gallery image add form"""

    title = _("New image")
    legend = _("Adding new gallery image")

    fields = field.Fields(IGalleryImageInfo)
    layout = getLayoutTemplate()
    parent_interface = IGalleryContainerTarget
    parent_view = GalleryContainerContentsView
    handle_upload = True

    def create(self, data):
        return GalleryImage()

    def add(self, image):
        data = self.request.form.get('form.widgets.image')
        filename = getattr(data, 'filename', None)
        if filename:
            filename = translateString(filename, escapeSlashes=True, forceLower=False, spaces='-')
            if not image.image_id:
                self._v_image_id = os.path.splitext(filename)[0]
            if filename in self.context:
                index = 2
                name = '%s-%d' % (filename, index)
                while name in self.context:
                    index += 1
                    name = '%s-%d' % (filename, index)
                filename = name
        if not filename:
            index = 1
            filename = 'image-%d' % index
            while filename in self.context:
                index += 1
                filename = 'image-%d' % index
        self.context[filename] = image

    def updateContent(self, object, data):
        super(GalleryImageAddForm, self).updateContent(object, data)
        if not object.image_id:
            object.image_id = getattr(self, '_v_image_id', None)


class GalleryContainerAddImagesFromArchiveMenuItem(JsMenuItem):
    """Resources from archive add menu item"""

    title = _(":: Add images from archive...")

    def render(self):
        ztfy_i18n.need()
        return super(GalleryContainerAddImagesFromArchiveMenuItem, self).render()


class IArchiveContentAddInfo(Interface):
    """Schema for images added from archives"""

    credit = TextLine(title=_("Author credit"),
                      description=_("Default author credits and copyright applied to all images"),
                      required=False)

    content = FileField(title=_("Archive data"),
                        description=_("Archive content's will be extracted as images ; format can be any ZIP, tar.gz or tar.bz2 file"),
                        required=True)


class GalleryContainerImagesFromArchiveAddForm(DialogAddForm):
    """Add a set of images from a single archive"""

    title = _("New images")
    legend = _("Adding new resources from archive file")

    fields = field.Fields(IArchiveContentAddInfo)
    layout = getLayoutTemplate()
    parent_interface = IGalleryContainerTarget
    parent_view = GalleryContainerContentsView
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
                image = GalleryImage()
                notify(ObjectCreatedEvent(image))
                self.context[name] = image
                image.credit = data.get('credit')
                image.image = content
                image.image_id = os.path.splitext(name)[0]


class GalleryImagePropertiesExtension(object):
    """Gallery image properties extension"""

    adapts(IGalleryImage, IZTFYBackLayer)
    implements(IGalleryImageExtension)

    title = _("Properties")
    icon = '/--static--/ztfy.blog/img/search.png'
    klass = 'search'
    weight = 1

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def url(self):
        return """javascript:$.ZTFY.dialog.open('%s/@@properties.html')""" % absoluteURL(self.context, self.request)


class GalleryImageTrashExtension(object):
    """Gallery image trash extension"""

    adapts(IGalleryImage, IZTFYBackLayer)
    implements(IGalleryImageExtension)

    title = _("Delete image")
    icon = '/--static--/ztfy.gallery.back/img/trash.png'
    klass = 'trash'
    weight = 99

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def url(self):
        intids = getUtility(IIntIds)
        return """javascript:$.ZBlog.gallery.remove(%d, '%s');""" % (intids.register(self.context),
                                                                     traversing_api.getName(self.context))


class GalleryImageEditForm(DialogEditForm):
    """Gallery image edit form"""

    legend = _("Edit image properties")

    fields = field.Fields(IGalleryImageInfo)
    layout = getLayoutTemplate()
    parent_interface = IGalleryContainerTarget
    parent_view = GalleryContainerContentsView
    handle_upload = True

    def getOutput(self, writer, parent, changes=()):
        status = changes and u'OK' or u'NONE'
        return writer.write({ 'output': status })


class GalleryImageDiapoView(BrowserView):
    """Display gallery image as diapo"""

    def __call__(self):
        self.update()
        return self.render()

    def update(self):
        pass

    render = getViewTemplate()


class GalleryImageIndexView(BrowserPage):
    """Gallery image default view"""

    def __call__(self):
        return queryMultiAdapter((self.context.image, self.request), Interface, 'index.html')()
