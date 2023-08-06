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
from persistent import Persistent

# import Zope3 interfaces
from zope.annotation.interfaces import IAnnotations

# import local interfaces
from ztfy.blog.interfaces.site import ISiteManager
from ztfy.gallery.interfaces import IGalleryManagerPaypalInfo, IGalleryImage, IGalleryImagePaypalInfo

# import Zope3 packages
from zope.component import adapter
from zope.container.contained import Contained
from zope.interface import implementer, implements
from zope.location import locate
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.i18n.property import I18nTextProperty, I18nImageProperty


class SiteManagerPaypalInfo(Persistent, Contained):

    implements(IGalleryManagerPaypalInfo)

    paypal_enabled = FieldProperty(IGalleryManagerPaypalInfo['paypal_enabled'])
    paypal_currency = FieldProperty(IGalleryManagerPaypalInfo['paypal_currency'])
    paypal_button_id = FieldProperty(IGalleryManagerPaypalInfo['paypal_button_id'])
    paypal_format_options = I18nTextProperty(IGalleryManagerPaypalInfo['paypal_format_options'])
    paypal_options_label = I18nTextProperty(IGalleryManagerPaypalInfo['paypal_options_label'])
    paypal_options_options = I18nTextProperty(IGalleryManagerPaypalInfo['paypal_options_options'])
    paypal_image_field_name = FieldProperty(IGalleryManagerPaypalInfo['paypal_image_field_name'])
    paypal_image_field_label = I18nTextProperty(IGalleryManagerPaypalInfo['paypal_image_field_label'])
    add_to_basket_button = I18nImageProperty(IGalleryManagerPaypalInfo['add_to_basket_button'])
    see_basket_button = I18nImageProperty(IGalleryManagerPaypalInfo['see_basket_button'])
    paypal_pkcs_key = FieldProperty(IGalleryManagerPaypalInfo['paypal_pkcs_key'])


PAYPAL_SITE_ANNOTATIONS_KEY = 'ztfy.gallery.sitemanager.paypal'

@adapter(ISiteManager)
@implementer(IGalleryManagerPaypalInfo)
def SiteManagerPaypalFactory(context):
    annotations = IAnnotations(context)
    info = annotations.get(PAYPAL_SITE_ANNOTATIONS_KEY)
    if info is None:
        info = annotations[PAYPAL_SITE_ANNOTATIONS_KEY] = SiteManagerPaypalInfo()
        locate(info, context, '++paypal++')
    return info


class GalleryImagePaypalInfo(Persistent, Contained):

    implements(IGalleryImagePaypalInfo)

    paypal_enabled = FieldProperty(IGalleryImagePaypalInfo['paypal_enabled'])
    paypal_disabled_message = I18nTextProperty(IGalleryImagePaypalInfo['paypal_disabled_message'])


PAYPAL_IMAGE_ANNOTATIONS_KEY = 'ztfy.gallery.image.paypal'

@adapter(IGalleryImage)
@implementer(IGalleryImagePaypalInfo)
def GalleryImagePaypalFactory(context):
    annotations = IAnnotations(context)
    info = annotations.get(PAYPAL_IMAGE_ANNOTATIONS_KEY)
    if info is None:
        info = annotations[PAYPAL_IMAGE_ANNOTATIONS_KEY] = GalleryImagePaypalInfo()
        locate(info, context, '++paypal++')
    return info
