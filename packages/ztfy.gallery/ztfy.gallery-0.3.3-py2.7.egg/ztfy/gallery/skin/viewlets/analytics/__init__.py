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

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces
from zope.intid.interfaces import IIntIds

# import local interfaces
from ztfy.gallery.skin.layer import IGalleryLayer

# import Zope3 packages
from zope.component import adapts, getUtility
from zope.interface import Interface

# import local packages
from ztfy.blog.defaultskin.viewlets.google.analytics import GoogleAnalyticsContentProvider
from ztfy.gallery.skin.search import SiteManagerSearchView


class SiteSearchGoogleAnalyticsContentProvider(GoogleAnalyticsContentProvider):
    """Site search Google Analytics content provider"""

    adapts(Interface, IGalleryLayer, SiteManagerSearchView)
