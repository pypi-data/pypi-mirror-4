### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2012 Thierry Florac <tflorac AT ulthar.net>
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
from ztfy.skin.viewlet import ViewletBase

__docformat__ = "restructuredtext"

# import standard packages
import chardet
import codecs
import csv
from cStringIO import StringIO

# import Zope3 interfaces
from z3c.language.switch.interfaces import II18n
from zope.traversing.interfaces import TraversalError

# import local interfaces
from ztfy.file.interfaces import IImageDisplay
from ztfy.gallery.interfaces import IGalleryIndexUploadData, IGalleryContainerTarget, IGalleryContainer, \
                                    IGalleryIndex, IGalleryImage, IGalleryImageExtension, IGalleryImageIndexInfo, \
                                    IGalleryIndexManager
from ztfy.skin.layer import IZTFYBackLayer

# import Zope3 packages
from z3c.form import field
from z3c.template.template import getLayoutTemplate
from zope.component import adapts
from zope.interface import implements
from zope.traversing import namespace
from zope.traversing.api import getParent
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.gallery.browser.gallery import GalleryContainerContentsView
from ztfy.gallery.index import GalleryIndexEntry
from ztfy.skin.form import DialogAddForm, DialogDisplayForm, DialogEditForm
from ztfy.skin.menu import DialogMenuItem

from ztfy.gallery import _


class GalleryIndexNamespaceTraverser(namespace.view):
    """++index++ namespace"""

    def traverse(self, name, ignored):
        result = IGalleryIndex(self.context, None)
        if result is not None:
            return result
        raise TraversalError('++index++')


class GalleryIndexAddForm(DialogAddForm):
    """Gallery index add form"""

    legend = _("Adding new gallery index from CSV file")

    fields = field.Fields(IGalleryIndexUploadData)
    layout = getLayoutTemplate()
    parent_interface = IGalleryContainerTarget
    parent_view = GalleryContainerContentsView
    handle_upload = True

    def createAndAdd(self, data):
        gallery = IGalleryContainer(self.context)
        index = IGalleryIndex(gallery, None)
        if index is not None:
            if data.get('clear'):
                index.clear()
            csv_data = data.get('data')
            # check for FileField tuple
            if isinstance(csv_data, tuple):
                csv_data = csv_data[0]
            encoding = data.get('encoding')
            if not encoding:
                encoding = chardet.detect(csv_data).get('encoding', 'utf-8')
            language = data.get('language')
            if encoding != 'utf-8':
                csv_data = codecs.getreader(encoding)(StringIO(csv_data)).read().encode('utf-8')
            values = index.values or {}
            if data.get('headers'):
                reader = csv.DictReader(StringIO(csv_data),
                                        delimiter=str(data.get('delimiter')),
                                        quotechar=str(data.get('quotechar')))
                for row in reader:
                    key = unicode(row['id'])
                    entry = values.get(key)
                    if entry is None:
                        entry = GalleryIndexEntry()
                    title = entry.title.copy()
                    title.update({ language: unicode(row.get('title'), 'utf-8') })
                    entry.title = title
                    description = entry.description.copy()
                    description.update({ language: unicode(row.get('description'), 'utf-8') })
                    entry.description = description
                    values[key] = entry
            else:
                reader = csv.reader(StringIO(csv_data),
                                    delimiter=str(data.get('delimiter')),
                                    quotechar=str(data.get('quotechar')))
                for row in reader:
                    key = unicode(row[0])
                    entry = values.get(key)
                    if entry is None:
                        entry = GalleryIndexEntry()
                    title = entry.title.copy()
                    title.update({ language: unicode(row[1], 'utf-8') })
                    entry.title = title
                    description = entry.description.copy()
                    description.update({ language: unicode(row[2], 'utf-8') })
                    entry.description = description
                    values[key] = entry
            index.values = values


class GalleryIndexAddMenuItem(DialogMenuItem):
    """Gallery index add menu item"""

    title = _(":: Add gallery index...")
    target = GalleryIndexAddForm


class GalleryIndexContentsView(DialogDisplayForm):
    """Gallery index contents"""

    @property
    def title(self):
        target = getParent(self.context, IGalleryContainerTarget)
        i18n = II18n(target, None)
        if i18n is not None:
            return i18n.queryAttribute('title', request=self.request)

    legend = _("Gallery index contents")


class GalleryImageIndexExtension(object):
    """Gallery image index extension"""

    adapts(IGalleryImage, IZTFYBackLayer)
    implements(IGalleryImageExtension)

    title = _("Index")
    icon = '/--static--/ztfy.gallery.back/img/index.png'
    klass = 'index'
    weight = 10

    def __new__(self, context, request):
        if not IGalleryIndexManager.providedBy(getParent(context)):
            return None
        return object.__new__(self, context, request)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def url(self):
        return """javascript:$.ZTFY.dialog.open('%s/@@indexProperties.html')""" % absoluteURL(self.context, self.request)


class GalleryImageIndexEditForm(DialogEditForm):
    """Gallery image index edit form"""

    legend = _("Edit image index properties")

    fields = field.Fields(IGalleryImageIndexInfo)
    layout = getLayoutTemplate()
    parent_interface = IGalleryContainerTarget
    parent_view = None


class GalleryImageIndexPrefix(ViewletBase):
    """Index widgets prefix"""

    @property
    def display(self):
        img = self.context
        return IImageDisplay(img.image).getDisplay('800x600')
