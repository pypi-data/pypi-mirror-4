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
from ztfy.gallery.interfaces import IGalleryParagraphInfo

# import Zope3 packages
from z3c.form import field

# import local packages
from ztfy.blog.browser.paragraph import BaseParagraphAddForm, BaseParagraphEditForm
from ztfy.gallery.paragraph import GalleryParagraph
from ztfy.i18n.browser import ztfy_i18n
from ztfy.skin.menu import JsMenuItem

from ztfy.gallery import _


class GalleryParagraphAddMenuItem(JsMenuItem):
    """Gallery paragraph add menu"""

    title = _(":: Add link to images gallery...")

    def render(self):
        ztfy_i18n.need()
        return super(GalleryParagraphAddMenuItem, self).render()


class GalleryParagraphAddForm(BaseParagraphAddForm):
    """Gallery paragraph add form"""

    title = _("New images gallery paragraph")
    legend = _("Creating a paragraph to display images gallery")

    fields = field.Fields(IGalleryParagraphInfo).omit('renderer')

    def create(self, data):
        return GalleryParagraph()


class GalleryParagraphEditForm(BaseParagraphEditForm):
    """Gallery paragraph edit form"""

    legend = _("Edit gallery display properties")

    fields = field.Fields(IGalleryParagraphInfo)
