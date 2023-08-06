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
from copy import copy

# import Zope3 interfaces
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.schema.interfaces import IVocabularyFactory

# import local interfaces
from ztfy.gallery.interfaces import IGalleryParagraphRenderer
from ztfy.skin.interfaces import ISkinnable

# import Zope3 packages
from zope.component import getAdapters, queryUtility
from zope.i18n import translate
from zope.interface import classProvides
from zope.publisher.browser import applySkin
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

# import local packages
from ztfy.utils.request import getRequest
from ztfy.utils.traversing import getParent


class GalleryParagraphRenderersVocabulary(SimpleVocabulary):

    classProvides(IVocabularyFactory)

    interface = IGalleryParagraphRenderer

    def __init__(self, context):
        request = getRequest()
        fake = copy(request)
        parent = getParent(context, ISkinnable)
        if parent is not None:
            skin = queryUtility(IBrowserSkinType, parent.getSkin())
            if skin is not None:
                applySkin(fake, skin)
            adapters = ((name, translate(adapter.label, context=request))
                        for (name, adapter) in getAdapters((context, fake), self.interface))
            terms = [SimpleTerm(name, name, title) for name, title in adapters]
        else:
            terms = []
        super(GalleryParagraphRenderersVocabulary, self).__init__(terms)
