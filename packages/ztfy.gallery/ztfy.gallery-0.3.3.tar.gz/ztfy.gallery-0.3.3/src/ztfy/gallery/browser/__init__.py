### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2011 Thierry Florac <tflorac AT ulthar.net>
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
from fanstatic import Library, Resource

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages
from ztfy.blog.browser import ztfy_blog_back
from ztfy.jqueryui import jquery_fancybox


library = Library('ztfy.gallery.back', 'resources')

ztfy_gallery_back_css = Resource(library, 'css/gallery.back.css',
                                 minified='css/gallery.back.min.css')

ztfy_gallery_back = Resource(library, 'js/gallery.back.js',
                             minified='js/gallery.back.min.js',
                             depends=[ztfy_gallery_back_css, ztfy_blog_back, jquery_fancybox],
                             bottom=True)
