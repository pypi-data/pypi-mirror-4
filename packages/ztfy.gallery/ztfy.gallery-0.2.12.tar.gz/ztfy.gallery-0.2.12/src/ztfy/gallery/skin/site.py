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
from z3c.json.interfaces import IJSONWriter
from z3c.language.switch.interfaces import II18n
from zope.annotation.interfaces import IAnnotations
from zope.catalog.interfaces import ICatalog
from zope.intid.interfaces import IIntIds
from zope.publisher.interfaces import NotFound

# import local interfaces
from interfaces import IHomeBackgroundManager
from interfaces import ISiteManagerPresentationInfo, ISiteManagerPresentation
from layer import IGalleryLayer
from ztfy.blog.browser.interfaces.skin import IPresentationTarget
from ztfy.blog.interfaces.category import ICategorizedContent
from ztfy.blog.interfaces.site import ISiteManager
from ztfy.file.interfaces import IImageDisplay
from ztfy.workflow.interfaces import IWorkflowContent

# import Zope3 packages
from zope.component import adapter, adapts, getUtility, queryMultiAdapter, queryUtility
from zope.container.contained import Contained
from zope.interface import implementer, implements, Interface
from zope.location import locate
from zope.publisher.browser import BrowserPage
from zope.schema.fieldproperty import FieldProperty
from zope.traversing.browser import absoluteURL

# import local packages
from menu import GallerySkinJsMenuItem
from ztfy.blog.browser import ztfy_blog_back
from ztfy.blog.browser.site import BaseSiteManagerIndexView
from ztfy.blog.defaultskin.site import SiteManagerRssView as BaseSiteManagerRssView
from ztfy.file.property import ImageProperty
from ztfy.jqueryui import jquery_multiselect

from ztfy.gallery import _


SITE_MANAGER_PRESENTATION_KEY = 'ztfy.gallery.presentation'


class SiteManagerPresentationViewMenuItem(GallerySkinJsMenuItem):
    """Site manager presentation menu item"""

    title = _(" :: Presentation model...")

    def render(self):
        jquery_multiselect.need()
        ztfy_blog_back.need()
        return GallerySkinJsMenuItem.render(self)


class SiteManagerPresentation(Persistent, Contained):
    """Site manager presentation infos"""

    implements(ISiteManagerPresentation)

    site_icon = ImageProperty(ISiteManagerPresentation['site_icon'])
    site_logo = ImageProperty(ISiteManagerPresentation['site_logo'])
    site_watermark = ImageProperty(ISiteManagerPresentation['site_watermark'])
    news_blog_oid = FieldProperty(ISiteManagerPresentation['news_blog_oid'])
    news_entries = FieldProperty(ISiteManagerPresentation['news_entries'])
    reports_blog_oid = FieldProperty(ISiteManagerPresentation['reports_blog_oid'])
    footer_section_oid = FieldProperty(ISiteManagerPresentation['footer_section_oid'])
    facebook_app_id = FieldProperty(ISiteManagerPresentation['facebook_app_id'])
    disqus_site_id = FieldProperty(ISiteManagerPresentation['disqus_site_id'])

    @property
    def news_blog(self):
        if not self.news_blog_oid:
            return None
        intids = getUtility(IIntIds)
        return intids.queryObject(self.news_blog_oid)

    @property
    def reports_blog(self):
        if not self.reports_blog_oid:
            return None
        intids = getUtility(IIntIds)
        return intids.queryObject(self.reports_blog_oid)

    @property
    def footer_section(self):
        if not self.footer_section_oid:
            return None
        intids = getUtility(IIntIds)
        return intids.queryObject(self.footer_section_oid)


@adapter(ISiteManager)
@implementer(ISiteManagerPresentation)
def SiteManagerPresentationFactory(context):
    annotations = IAnnotations(context)
    presentation = annotations.get(SITE_MANAGER_PRESENTATION_KEY)
    if presentation is None:
        presentation = annotations[SITE_MANAGER_PRESENTATION_KEY] = SiteManagerPresentation()
        locate(presentation, context, '++presentation++')
    return presentation


class SiteManagerPresentationTargetAdapter(object):

    adapts(ISiteManager, IGalleryLayer)
    implements(IPresentationTarget)

    target_interface = ISiteManagerPresentationInfo

    def __init__(self, context, request):
        self.context, self.request = context, request


class SiteManagerIndexView(BaseSiteManagerIndexView):
    """Site manager index page"""

    @property
    def background_image(self):
        manager = IHomeBackgroundManager(self.context, None)
        if manager is not None:
            return manager.getImage()

    @property
    def categories(self):
        catalog = queryUtility(ICatalog, 'Catalog')
        if catalog is not None:
            index = catalog.get('categories')
            if index is not None:
                intids = getUtility(IIntIds)
                return sorted(((id, intids.queryObject(id)) for id in index.values()),
                              key=lambda x: II18n(x[1]).queryAttribute('shortname', request=self.request))
        return []

    @property
    def reports(self):
        target = self.presentation.reports_blog
        if (target is not None) and target.visible:
            return target.getVisibleTopics()[:4]
        else:
            return []

    @property
    def news(self):
        target = self.presentation.news_blog
        if (target is not None) and target.visible:
            return target.getVisibleTopics()[:self.presentation.news_entries]
        else:
            return []

    def getCategory(self, topic):
        categories = ICategorizedContent(topic).categories
        if not categories:
            return ''
        return ' - '.join(('<a href="%s">%s</a>' % (absoluteURL(category, self.request),
                                                    II18n(category).queryAttribute('shortname', request=self.request)) for category in categories))


class SiteManagerRssView(BaseSiteManagerRssView):

    @property
    def topics(self):
        result = []
        target = self.presentation.reports_blog
        if (target is not None) and target.visible:
            result.extend(target.getVisibleTopics())
        target = self.presentation.news_blog
        if (target is not None) and target.visible:
            result.extend(target.getVisibleTopics())
        result.sort(key=lambda x: IWorkflowContent(x).publication_effective_date, reverse=True)
        return result[:self.presentation.news_entries + 4]


class SiteManagerBackgroundURL(BrowserPage):

    def __call__(self):
        writer = getUtility(IJSONWriter)
        image = self.background_image
        if image is not None:
            self.request.response.setHeader('Cache-Control', 'private, no-cache, no-store')
            self.request.response.setHeader('Pragma', 'no-cache')
            display = IImageDisplay(image.image).getDisplay('w1024')
            if display is not None:
                return writer.write({ 'url': absoluteURL(display, self.request),
                                      'title': II18n(image).queryAttribute('title', request=self.request) })
        return writer.write('none')

    @property
    def background_image(self):
        manager = IHomeBackgroundManager(self.context, None)
        if manager is not None:
            return manager.getImage()


class SiteManagerIconView(BrowserPage):
    """'favicon.ico' site view"""

    def __call__(self):
        icon = ISiteManagerPresentation(self.context).site_icon
        if icon is not None:
            view = queryMultiAdapter((icon, self.request), Interface, 'index.html')
            if view is not None:
                return view()
        raise NotFound(self.context, 'favicon.ico', self.request)
