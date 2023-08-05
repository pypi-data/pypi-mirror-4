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
from ztfy.gallery.interfaces import IGalleryParagraph, IGalleryParagraphRenderer

# import Zope3 packages
from zope.component import adapts
from zope.interface import implements

# import local packages
from ztfy.gallery.defaultskin.renderers.default import DefaultGalleryParagraphRenderer
from ztfy.gallery.skin.layer import IGalleryLayer

from ztfy.gallery import _


class GalleryParagraphRenderer(DefaultGalleryParagraphRenderer):

    adapts(IGalleryParagraph, IGalleryLayer)
    implements(IGalleryParagraphRenderer)

    label = _("Gallery renderer with scrollable pages of slides")

    @property
    def pages(self):
        index = 0
        images = self.gallery.getVisibleImages()
        length = len(images)
        while index < length:
            yield(images[index:index + 15])
            index += 15


class SingleImageParagraphRenderer(DefaultGalleryParagraphRenderer):

    adapts(IGalleryParagraph, IGalleryLayer)
    implements(IGalleryParagraphRenderer)

    label = _("Scrollable pages with a single image for each page")
