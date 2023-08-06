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
from ztfy.blog.defaultskin.layer import IZBlogDefaultLayer, IZBlogDefaultSkin

# import Zope3 packages
from zope.schema import TextLine

# import local packages

from ztfy.gallery import _


class IGalleryLayer(IZBlogDefaultLayer):
    """Gallery layer - inherited from ZBlog default layer"""


class IGallerySkin(IZBlogDefaultSkin, IGalleryLayer):
    """Gallery skin - inherited from ZBlog default skin"""

    label = TextLine(title=_("Gallery skin"))
