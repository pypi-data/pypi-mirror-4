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
from hurry.query.interfaces import IQuery
from zope.intid.interfaces import IIntIds
from zope.session.interfaces import ISession

# import local interfaces
from ztfy.blog.interfaces.category import ICategorizedContent
from ztfy.blog.interfaces.topic import ITopic
from ztfy.workflow.interfaces import IWorkflowContent

# import Zope3 packages
from hurry.query import And
from hurry.query.set import AnyOf
from hurry.query.value import Eq
from zope.component import getUtility
from zope.traversing.browser.absoluteurl import absoluteURL

# import local packages
from ztfy.skin.page import TemplateBasedPage
from ztfy.utils.catalog.index import Text
from ztfy.utils.traversing import getParent


SITE_MANAGER_SESSION_ID = 'ztfy.gallery.site.search'

class SiteManagerSearchView(TemplateBasedPage):
    """Site manager search page"""

    def __call__(self):
        form = self.request.form
        if 'page' in form:
            session = ISession(self.request)[SITE_MANAGER_SESSION_ID]
            self.search_text = search_text = session.get('search_text', '')
            self.search_tag = search_tag = session.get('search_tag', '') or None
        else:
            self.search_text = search_text = form.get('search_text', '').strip()
            self.search_tag = search_tag = form.get('search_tag', '') or None
        if not search_text:
            if not search_tag:
                self.request.response.redirect(absoluteURL(self.context, self.request))
                return ''
            else:
                intids = getUtility(IIntIds)
                category = intids.queryObject(search_tag)
                self.request.response.redirect(absoluteURL(category, self.request))
                return ''
        return super(SiteManagerSearchView, self).__call__()

    def update(self):
        super(SiteManagerSearchView, self).update()
        query = getUtility(IQuery)
        # Search for matching images
        params = []
        params.append(Text(('Catalog', 'image_title'), { 'query': ' '.join(('%s*' % m for m in self.search_text.split())),
                                                         'autoexpand': 'on_miss',
                                                         'ranking': True }))
        # .. get and filter search results
        topics = {}
        [ topics.setdefault(getParent(image, ITopic), []).append(image)
          for image in query.searchResults(And(*params)) ]
        if self.search_tag:
            for topic in topics.keys()[:]:
                ids = ICategorizedContent(topic).categories_ids
                if ids and (self.search_tag not in ids):
                    del topics[topic]

        # Search for matching topics
        params = []
        params.append(Eq(('Catalog', 'content_type'), 'ITopic'))
        params.append(Text(('Catalog', 'title'), { 'query': ' '.join(('%s*' % m for m in self.search_text.split())),
                                                   'autoexpand': 'on_miss',
                                                   'ranking': True }))
        if self.search_tag:
            intids = getUtility(IIntIds)
            self.category = intids.queryObject(self.search_tag)
            params.append(AnyOf(('Catalog', 'categories'), (self.search_tag,)))
        # .. get search results
        [ topics.setdefault(topic, []) for topic in query.searchResults(And(*params)) ]

        # .. check topics status and sort
        for topic in topics.keys()[:]:
            if not IWorkflowContent(topic).isVisible():
                del topics[topic]
        results = sorted(((topic, topics[topic]) for topic in topics),
                         key=lambda x: IWorkflowContent(x[0]).publication_effective_date,
                         reverse=True)

        # .. store search settings in session
        session = ISession(self.request)[SITE_MANAGER_SESSION_ID]
        session['search_text'] = self.search_text
        session['search_tag'] = self.search_tag

        # .. handle pagination
        page = int(self.request.form.get('page', 0))
        page_length = 10
        first = page_length * page
        last = first + page_length - 1
        pages = len(results) / page_length
        if len(results) % page_length:
            pages += 1

        self.results = { 'results': results[first:last + 1],
                         'pages': pages,
                         'first': first,
                         'last': last,
                         'has_prev': page > 0,
                         'has_next': last < len(results) - 1 }
