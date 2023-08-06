# -*- coding: utf-8 -*-
# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-seo views/forms/actions/components for web ui"""

from cubicweb.view import View
from cubicweb.selectors import none_rset
from cubicweb.appobject import AppObject
from cubicweb.web.views.urlrewrite import SimpleReqRewriter, rgx

class SeoReqRewriter(SimpleReqRewriter):
    rules = [
        (rgx('/robots.txt$'), dict(vid='robotstxt')),
        (rgx('/sitemap.xml$'), dict(vid='sitemapxml')),
        ]

class RobotsRule(AppObject):
    """abstract base class for robots rules

    A custom rule should be built by extending this class. For instance::

      from cubes.seo.views import RobotsRule

      class VcsfileRobotsRule(RobotsRule):
          __regid__ = 'vcsfile'
          STANZA = ['User-Agent: *',
                    'Disallow: /versioncontent',
                    'Disallow: /testexecution',
                    'Disallow: /versionedfile',
                    'Disallow: /deletedversioncontent']

    To get more control, override the items() method.
    """
    __registry__ = 'robotstxt'
    __abstract__ = True
    STANZA = []

    def stanza(self):
        return u'\n'.join(self.STANZA)

class CwRobotsRule(RobotsRule):
    __regid__ = 'cubicweb.admin'
    STANZA =  ["User-Agent: *",
               "Disallow: /schema",
               "Disallow: /cwetype",
               "Disallow: /cwrtype",
               "Disallow: /search",
               "Disallow: /login",
               "Disallow: /cwuser",
               "Disallow: /cwgroup",
               "Disallow: /cwsource",
               "Disallow: /_registry",
               "Disallow: /siteconfig",
               "Disallow: /siteinfo",
               "Disallow: /notfound",
               "Disallow: /processinfo",
               "Disallow: /changelog",
               "Disallow: /add/",
               ]

class RobotsTxt(View):
    """A view that implements the http://robotstxt.org standard"""
    __regid__ = 'robotstxt'
    content_type = 'text/plain'
    templatable = False
    __select__ = none_rset()

    def call(self):
        self.w(u'Sitemap: %s\n\n' % self._cw.build_url('sitemap.xml'))
        if 'robotstxt' in self._cw.vreg: # XXX or make sure it exists by creating it in this cube...
            for rule in self._cw.vreg['robotstxt'].possible_objects(self._cw):
                self.w(rule.stanza())
                self.w(u'\n')

CHANGEFREQS = frozenset(('always', 'hourly', 'daily', 'weekly', 'monthly', 'yearly', 'never'))

class SitemapRule(AppObject):
    """abstract base class for sitemap rules

    A custom rule should be built by extending this class. For instance::

      from cubes.seo.views import SitemapRule

      class CardSitemapRule(SitemapRule):
          __regid__ = 'card'
          query = 'Any X WHERE X is Card'
          priority = 1.0
          chfreq = 'monthly'

    To get more control, override the items() method.
    """
    __registry__ = 'sitemap'
    __abstract__ = True
    query = None
    priority = None # optional
    chfreq = None   # optional

    def items(self):
        rset = self._cw.execute(self.query)
        for item in rset.entities():
            yield (item.absolute_url(), item.modification_date, self.chfreq, self.priority)

class Sitemaps(View):
    """A view that implements the http://sitemaps.org standard

    Content types must append rules to the sitemap registry in order to appear
    in the list at /sitemap.xml.
    """

    __regid__ = 'sitemapxml'
    content_type = 'text/xml'
    templatable = False
    __select__ = none_rset()

    def add_url(self, url, lastmod=None, chfreq=None, priority=None):
        self.w(u'<url><loc>%s</loc>' % url)
        if lastmod:
            self.w(u'<lastmod>%s</lastmod>' % lastmod.strftime('%Y-%m-%d'))
        if chfreq:
            if chfreq in CHANGEFREQS:
                self.w(u'<changefreq>%s</changefreq>' % chfreq)
            else:
                self.warning('url %s gave %s which is not a valid changefreq according to http://sitemaps.org'
                             % (url, chfreq))
        if priority:
            if 0 <= float(priority) <= 1:
                self.w(u'<priority>%.2f</priority>' % priority)
            else:
                self.warning('url %s gave %s which is not a valid priority according to http://sitemaps.org'
                             % (url, priority))
        self.w(u'</url>')

    def call(self):
        # XXX have a look at databnf/file/stable/sitemap.py for cases where the sitemap file is
        # too big (>10Mb) or has too many entries (>50k)
        self.w(u'<?xml version="1.0" encoding="%s"?>\n' % self._cw.encoding)
        self.w(u'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        self.add_url(self._cw.base_url())
        if 'sitemap' in self._cw.vreg: # XXX or make sure it exists by creating it in this cube...
            count = 0
            for rule in self._cw.vreg['sitemap'].possible_objects(self._cw):
                for item in rule.items():
                    self.add_url(*item)
                    count += 1
                    if count > 50000:
                        self.warning('too many items for this sitemap (limit is 50,000)')
                        break
                if count > 50000:
                    break
        else:
            self.debug('no sitemap registry found')
        self.w(u'</urlset>')
