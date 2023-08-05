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
from interfaces import IFooterViewletManager
from ztfy.blog.interfaces.site import ISiteManager
from ztfy.gallery.skin.interfaces import ISiteManagerPresentation

# import Zope3 packages
from zope.interface import implements
from zope.viewlet.manager import WeightOrderedViewletManager

# import local packages
from ztfy.blog.browser.viewlets import BaseViewlet
from ztfy.utils.traversing import getParent


class FooterViewletManager(WeightOrderedViewletManager):

    implements(IFooterViewletManager)


class FooterViewlet(BaseViewlet):
    """Footer viewlet"""

    site_presentation = None

    def update(self):
        super(FooterViewlet, self).update()
        site = getParent(self.context, ISiteManager)
        if site is not None:
            self.site_presentation = ISiteManagerPresentation(site)
