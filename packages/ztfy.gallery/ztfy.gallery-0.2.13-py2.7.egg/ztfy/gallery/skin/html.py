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
from zope.schema.interfaces import IText

# import local interfaces
from ztfy.file.browser.widget.interfaces import IHTMLWidgetSettings
from ztfy.gallery.skin.layer import IGalleryLayer
from ztfy.skin.interfaces import IBaseForm

# import Zope3 packages
from zope.component import adapts
from zope.interface import implements

# import local packages
from ztfy.blog.browser.skin import HTMLWidgetAdapter as BaseHTMLWidgetAdapter


class HTMLWidgetAdapter(BaseHTMLWidgetAdapter):
    """Custom HTML widget settings adapter"""

    adapts(IText, IBaseForm, IGalleryLayer)
    implements(IHTMLWidgetSettings)

    @property
    def mce_content_css(self):
        return '/--static--/ztfy.gallery/css/gallery.css'
