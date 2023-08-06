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
from ztfy.blog.defaultskin.layer import IZBlogDefaultLayer
from ztfy.blog.interfaces.site import ISiteManager
from ztfy.gallery.interfaces import IGalleryContainer, IGalleryParagraph, IGalleryParagraphRenderer, IGalleryManagerPaypalInfo

# import Zope3 packages
from z3c.template.template import getViewTemplate
from zope.component import adapts
from zope.interface import implements
from zope.traversing import api as traversing_api

# import local packages
from ztfy.gallery.defaultskin import ztfy_gallery_defaultskin_css
from ztfy.jqueryui import jquery_tools_12, jquery_fancybox
from ztfy.utils.request import setRequestData
from ztfy.utils.traversing import getParent

from ztfy.gallery import _


class DefaultGalleryParagraphRenderer(object):

    adapts(IGalleryParagraph, IZBlogDefaultLayer)
    implements(IGalleryParagraphRenderer)

    label = _("Default gallery renderer with small slides")

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def update(self):
        self.gallery = IGalleryContainer(traversing_api.getParent(self.context))
        ztfy_gallery_defaultskin_css.need()
        jquery_tools_12.need()
        jquery_fancybox.need()

    render = getViewTemplate()

    @property
    def paypal(self):
        site = getParent(self.context, ISiteManager)
        info = IGalleryManagerPaypalInfo(site)
        setRequestData('gallery.paypal', info, self.request)
        return info
