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
from zope.container.interfaces import IContained

# import local interfaces
from ztfy.blog.interfaces.paragraph import IParagraphInfo, IParagraphWriter, IParagraph
from ztfy.i18n.interfaces import II18nAttributesAware
from ztfy.skin.interfaces import IOrderedContainer

# import Zope3 packages
from zope.container.constraints import contains, containers
from zope.interface import Interface
from zope.schema import Int, Bool, Text, TextLine, URI, Choice, List, Dict, Object

# import local packages
from ztfy.file.schema import ImageField, FileField
from ztfy.i18n.schema import I18nText, I18nTextLine, I18nImage
from ztfy.utils.encoding import EncodingField

from ztfy.gallery import _


class IGalleryNamespaceTarget(Interface):
    """Marker interface for targets handling '++gallery++' namespace traverser"""


class IGalleryImageBaseInfo(II18nAttributesAware):
    """Gallery image base interface"""

    title = I18nTextLine(title=_("Title"),
                         description=_("Image's title"),
                         required=False)

    description = I18nText(title=_("Description"),
                           description=_("Short description of the image"),
                           required=False)


class IGalleryImageInfo(IGalleryImageBaseInfo):
    """Gallery image infos interface"""

    credit = TextLine(title=_("Author credit"),
                      description=_("Credit and copyright notices of the image"),
                      required=False)

    image = ImageField(title=_("Image data"),
                       description=_("Current content of the image"),
                       required=True)

    image_id = TextLine(title=_("Image ID"),
                        description=_("Unique identifier of this image in the whole collection"),
                        required=False)

    visible = Bool(title=_("Visible image ?"),
                   description=_("Select 'No' to hide this image"),
                   required=True,
                   default=True)

    def title_or_id():
        """Get image's title or ID"""


class IGalleryImage(IGalleryImageInfo, IContained):
    """Gallery image full interface"""

    containers('ztfy.gallery.interfaces.IGalleryContainer')


class IGalleryImageExtension(Interface):
    """Gallery image extension info"""

    title = TextLine(title=_("Extension title"),
                     required=True)

    url = TextLine(title=_("Extension view URL"),
                   required=True)

    icon = URI(title=_("Extension icon URL"),
               required=True)

    weight = Int(title=_("Extension weight"),
                 required=True,
                 default=50)


class IGalleryContainerInfo(Interface):
    """Gallery container base interface"""

    def getVisibleImages():
        """Get visible images in ordered list"""


class IGalleryContainer(IGalleryContainerInfo, IOrderedContainer, IGalleryNamespaceTarget):
    """Gallery images container interface"""

    contains(IGalleryImage)


class IGalleryContainerTarget(IGalleryNamespaceTarget):
    """Marker interface for gallery images container target"""


class IGalleryManagerPaypalInfo(II18nAttributesAware):
    """Global Paypal informations for site manager"""

    paypal_enabled = Bool(title=_("Enable Paypal payments"),
                          description=_("Enable or disable Paypal payments globally"),
                          required=True,
                          default=False)

    paypal_currency = TextLine(title=_("Paypal currency"),
                               description=_("Currency used for Paypal exchanges"),
                               required=False,
                               max_length=3,
                               default=u'EUR')

    paypal_button_id = TextLine(title=_("Paypal button ID"),
                                description=_("Internal number of Paypal registered payment button"),
                                required=False)

    paypal_format_options = I18nText(title=_("'Format' options"),
                                     description=_("Enter 'Format' options values ; values and labels may be separated by a '|'"),
                                     required=False)

    paypal_options_label = I18nTextLine(title=_("'Options' label"),
                                        description=_("Label applied to 'Options' selection box"),
                                        required=False)

    paypal_options_options = I18nText(title=_("'Options' options"),
                                      description=_("Enter 'Options' options values ; values and labels may be separated by '|'"),
                                      required=False)

    paypal_image_field_name = TextLine(title=_("Image ID field name"),
                                       description=_("Paypal ID of hidden field containing image ID"),
                                       required=False)

    paypal_image_field_label = I18nTextLine(title=_("Image ID field label"),
                                            description=_("Paypal label of field containing image ID"),
                                            required=False)

    add_to_basket_button = I18nImage(title=_("'Add to basket' image"),
                                     description=_("Image containing 'Add to basket' link"),
                                     required=False)

    see_basket_button = I18nImage(title=_("'See basket' image"),
                                  description=_("Image containing 'See basket' link"),
                                  required=False)

    paypal_pkcs_key = Text(title=_("Paypal basket PKCS key"),
                           description=_("Full PKCS key used to access Paypal basket"),
                           required=False)


class IGalleryImagePaypalInfo(II18nAttributesAware):
    """Gallery image Paypal informations for a single image"""

    paypal_enabled = Bool(title=_("Enable Paypal payments"),
                          description=_("Enable or disable Paypal payments for this image"),
                          required=True,
                          default=True)

    paypal_disabled_message = I18nText(title=_("Paypal disabled message"),
                                       description=_("Message displayed when Paypal is disabled for this picture"),
                                       required=False)


#
# Gallery paragraphs management
#

class IGalleryParagraphRenderer(Interface):
    """Gallery paragraph renderer"""

    label = TextLine(title=_("Renderer name"),
                     required=True)

    def update():
        """Update gallery paragraph renderer"""

    def render():
        """Render gallery paragraph renderer"""


class IGalleryParagraphInfo(IParagraphInfo):
    """Gallery link paragraph base interface"""

    renderer = Choice(title=_("Paragraph renderer"),
                      description=_("Renderer used to render this gallery"),
                      required=True,
                      default=u'default',
                      vocabulary="ZTFY Gallery renderers")


class IGalleryParagraphWriter(IParagraphWriter):
    """Gallery link paragraph writer interface"""


class IGalleryParagraph(IParagraph, IGalleryParagraphInfo, IGalleryParagraphWriter):
    """Gallery link interface full interface"""


#
# Gallery index interfaces
#

class IGalleryIndexUploadData(Interface):
    """Gallery index upload interface"""

    clear = Bool(title=_("Clear index before import ?"),
                 description=_("If 'Yes', index will be cleared before importing new file content"),
                 required=True,
                 default=False)

    data = FileField(title=_("Uploaded index data"),
                     description=_("Please select a CSV file containing images index"),
                     required=True)

    language = Choice(title=_("Index language"),
                      description=_("Language matching given index contents"),
                      required=True,
                      vocabulary="ZTFY base languages",
                      default=u'en')

    encoding = EncodingField(title=_("Data encoding"),
                             description=_("Encoding of the uploaded CSV file"),
                             required=False)

    headers = Bool(title=_("CSV header ?"),
                   description=_("Is the CSV file containing header line ?"),
                   required=True,
                   default=True)

    delimiter = TextLine(title=_("Fields delimiter"),
                         description=_("Character used to separate values in CSV file; use \\t for tabulation"),
                         max_length=2,
                         required=True,
                         default=u",")

    quotechar = TextLine(title=_("Quote character"),
                         description=_("Character used to quote fields containing special characters, such as fields delimiter"),
                         max_length=1,
                         required=True,
                         default=u'"')


class IGalleryIndexInfo(Interface):
    """Gallery index infos interface"""

    values = Dict(title=_("Gallery index values"),
                  key_type=TextLine(),
                  value_type=Object(schema=IGalleryImageBaseInfo),
                  required=False)


class IGalleryIndexWriter(Interface):
    """Gallery index writer interface"""

    def clear(self):
        """Clear index contents"""


class IGalleryIndex(IGalleryIndexInfo, IGalleryIndexWriter):
    """Gallery index full interface"""


class IGalleryIndexManager(Interface):
    """Marker interface for gallery container handling an index"""


class IGalleryImageIndexInfo(Interface):
    """Gallery image index infos interface"""

    ids = List(title=_("Index keys"),
               description=_("List of values matching gallery's index keys"),
               value_type=Choice(vocabulary="ZTFY gallery index"))
