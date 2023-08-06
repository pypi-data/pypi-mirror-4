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
from fanstatic import Library, Resource, Group

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages
from ztfy.blog.defaultskin import ztfy_blog_defaultskin_css, \
                                  ztfy_blog_defaultskin_base, \
                                  ztfy_blog_defaultskin
from ztfy.jqueryui import jquery_fancybox_css, jquery_fancybox
from ztfy.skin import ztfy_skin_base


library = Library('ztfy.gallery.defaultskin', 'resources')

ztfy_gallery_defaultskin_css = Resource(library, 'css/ztfy.gallery.css',
                                        minified='css/ztfy.gallery.min.css',
                                        depends=[])

ztfy_gallery_defaultskin_base = Resource(library, 'js/ztfy.gallery.js',
                                         minified='js/ztfy.gallery.min.js',
                                         depends=[ztfy_blog_defaultskin_base,
                                                  jquery_fancybox],
                                         bottom=True)

ztfy_gallery_defaultskin = Group(depends=[ztfy_blog_defaultskin,
                                          ztfy_gallery_defaultskin_css,
                                          ztfy_gallery_defaultskin_base])
