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
from ztfy.gallery.defaultskin import ztfy_gallery_defaultskin_css, \
                                     ztfy_gallery_defaultskin


library = Library('ztfy.gallery', 'resources')

ztfy_gallery_css = Resource(library, 'css/gallery.css', minified='css/gallery.min.css',
                            depends=[ztfy_gallery_defaultskin_css])

ztfy_gallery = Resource(library, 'js/gallery.js', minified='js/gallery.min.js',
                        depends=[ztfy_gallery_css, ztfy_gallery_defaultskin])
