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
from zopyx.txng3.core.interfaces.indexable import IIndexableContent

# import local interfaces
from ztfy.gallery.interfaces import IGalleryImage, IGalleryContainer, IGalleryContainerTarget

# import Zope3 packages
from zope.component import adapter, adapts
from zope.container.contained import Contained
from zope.interface import implementer, implements
from zope.location import locate
from zope.schema.fieldproperty import FieldProperty
from zopyx.txng3.core.content import IndexContentCollector

# import local packages
from ztfy.blog.ordered import OrderedContainer
from ztfy.extfile.blob import BlobImage
from ztfy.file.property import ImageProperty
from ztfy.i18n.property import I18nTextProperty


class GalleryImage(Persistent, Contained):

    implements(IGalleryImage)

    title = I18nTextProperty(IGalleryImage['title'])
    description = I18nTextProperty(IGalleryImage['description'])
    credit = FieldProperty(IGalleryImage['credit'])
    image = ImageProperty(IGalleryImage['image'], klass=BlobImage, img_klass=BlobImage)
    image_id = FieldProperty(IGalleryImage['image_id'])
    visible = FieldProperty(IGalleryImage['visible'])


class GalleryImageTextIndexer(object):

    adapts(IGalleryImage)
    implements(IIndexableContent)

    def __init__(self, context):
        self.context = context

    def indexableContent(self, fields):
        icc = IndexContentCollector()
        for field in fields:
            for lang, value in getattr(self.context, field, {}).items():
                if value:
                    icc.addContent(field, value, lang)
        return icc


class GalleryContainer(OrderedContainer):

    implements(IGalleryContainer)

    def getVisibleImages(self):
        return [img for img in self.values() if img.visible]


GALLERY_ANNOTATIONS_KEY = 'ztfy.gallery.container'

@adapter(IGalleryContainerTarget)
@implementer(IGalleryContainer)
def GalleryContainerFactory(context):
    """Gallery container adapter"""
    annotations = IAnnotations(context)
    container = annotations.get(GALLERY_ANNOTATIONS_KEY)
    if container is None:
        container = annotations[GALLERY_ANNOTATIONS_KEY] = GalleryContainer()
        locate(container, context, '++gallery++')
    return container
