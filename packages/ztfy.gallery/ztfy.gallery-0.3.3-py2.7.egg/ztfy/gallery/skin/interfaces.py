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
from ztfy.blog.browser.interfaces.skin import IBasePresentationInfo
from ztfy.blog.defaultskin.interfaces import ILLUSTRATION_DISPLAY_LEFT, ILLUSTRATION_DISPLAY_VOCABULARY
from ztfy.blog.interfaces.blog import IBlog
from ztfy.blog.interfaces.container import IOrderedContainer
from ztfy.blog.interfaces.section import ISection
from ztfy.i18n.interfaces import II18nAttributesAware

# import Zope3 packages
from zope.container.constraints import contains
from zope.interface import Interface
from zope.schema import Bool, Int, TextLine, List, Choice, Object

# import local packages
from ztfy.blog.schema import InternalReference
from ztfy.file.schema import ImageField
from ztfy.i18n.schema import I18nTextLine

from ztfy.gallery import _


#
# Site presentation management
#

class ISiteManagerPresentationInfo(IBasePresentationInfo):
    """Site manager presentation base interface"""

    site_icon = ImageField(title=_("Site icon"),
                           description=_("Site 'favicon' image"),
                           required=False)

    site_logo = ImageField(title=_("Site logo"),
                           description=_("Site logo displayed on home page"),
                           required=False)

    site_watermark = ImageField(title=_("Site watermark"),
                                description=_("Watermark image applied on gallery images"),
                                required=False)

    news_blog_oid = InternalReference(title=_("News blog OID"),
                                      description=_("Internal ID of news blog's target"),
                                      required=False)

    news_entries = Int(title=_("Displayed entries count"),
                       description=_("Number of news topics displayed in front-page"),
                       required=True,
                       default=10)

    reports_blog_oid = InternalReference(title=_("Reports blog OID"),
                                         description=_("Internal ID of reports blog's target"),
                                         required=False)

    footer_section_oid = InternalReference(title=_("Footer topics section OID"),
                                           description=_("Internal ID of section containing topics displayed in pages footer"),
                                           required=False)

    facebook_app_id = TextLine(title=_("Facebook application ID"),
                               description=_("Application ID declared on Facebook"),
                               required=False)

    disqus_site_id = TextLine(title=_("Disqus site ID"),
                              description=_("Site's ID on Disqus comment platform can be used to allow topics comments"),
                              required=False)


class ISiteManagerPresentation(ISiteManagerPresentationInfo):
    """Site manager presentation full interface"""

    news_blog = Object(title=_("News blog target"),
                       schema=IBlog,
                       readonly=True)

    reports_blog = Object(title=_("Reports blog target"),
                          schema=IBlog,
                          readonly=True)

    footer_section = Object(title=_("Footer section target"),
                            schema=ISection,
                            readonly=True)


#
# Home background images management
#

class IHomeBackgroundManagerDetailMenuTarget(Interface):
    """Marker interface for home background image add form menu target"""


class IHomeBackgroundImage(II18nAttributesAware):
    """Home background image interface"""

    title = I18nTextLine(title=_("Title"),
                         description=_("Image's title, as displayed in front page"),
                         required=True)

    image = ImageField(title=_("Image data"),
                       description=_("This attribute holds image data ; select an optimized image of 1024 pixels width"),
                       required=True)

    visible = Bool(title=_("Visible ?"),
                   description=_("Select 'No' to hide this image from home page"),
                   required=True,
                   default=True)


class IHomeBackgroundInfo(Interface):
    """Home background images manager infos interface"""

    def getImage():
        """Retrieve current image to display in home page background"""


class IHomeBackgroundManager(IHomeBackgroundInfo, IOrderedContainer):
    """Home background images manager interface"""

    contains(IHomeBackgroundImage)


class IHomeBackgroundManagerContentsView(Interface):
    """Background manager contents view marker interface"""


#
# Topic presentation management
#

class ITopicPresentationInfo(II18nAttributesAware, IBasePresentationInfo):
    """Topic presentation base interface"""

    publication_date = I18nTextLine(title=_("Displayed publication date"),
                                    description=_("Date at which this report was done"),
                                    required=False)

    header_format = Choice(title=_("Header format"),
                           description=_("Text format used for content's header"),
                           required=True,
                           default=u'zope.source.plaintext',
                           vocabulary='SourceTypes')

    display_googleplus = Bool(title=_("Display Google +1 button"),
                              description=_("Display Google +1 button next to content's title"),
                              required=True,
                              default=True)

    display_fb_like = Bool(title=_("Display Facebook 'like' button"),
                           description=_("Display Facebook 'like' button next to content's title"),
                           required=True,
                           default=True)

    illustration_position = Choice(title=_("Illustration's position"),
                                   description=_("Select position of topic's illustration"),
                                   required=True,
                                   default=ILLUSTRATION_DISPLAY_LEFT,
                                   vocabulary=ILLUSTRATION_DISPLAY_VOCABULARY)

    illustration_width = Int(title=_("Illustration's width"),
                             description=_("Display width of topic's illustration"),
                             required=True,
                             default=176)

    linked_resources = List(title=_("Downloadable resources"),
                            description=_("Select list of resources displayed as download links"),
                            required=False,
                            default=[],
                            value_type=Choice(vocabulary="ZTFY content resources"))


class ITopicPresentation(ITopicPresentationInfo):
    """Topic presentation full interface"""
