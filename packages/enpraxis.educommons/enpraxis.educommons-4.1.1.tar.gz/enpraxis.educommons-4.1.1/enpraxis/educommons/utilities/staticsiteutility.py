##################################################################################
#    Copyright (c) 2004-2009 Utah State University, All rights reserved. 
#    Portions copyright 2009 Massachusetts Institute of Technology, All rights reserved.
#                                                                                 
#    This program is free software; you can redistribute it and/or modify         
#    it under the terms of the GNU General Public License as published by         
#    the Free Software Foundation, version 2.                                      
#                                                                                 
#    This program is distributed in the hope that it will be useful,              
#    but WITHOUT ANY WARRANTY; without even the implied warranty of               
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                
#    GNU General Public License for more details.                                 
#                                                                                 
#    You should have received a copy of the GNU General Public License            
#    along with this program; if not, write to the Free Software                  
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA    
#                                                                                 
##################################################################################

__author__  = '''Brent Lambert, David Ray, Jon Thomas'''
__version__   = '$ Revision 0.0 $'[11:-2]

import re

from urlparse import urlparse, urlunparse, urlsplit

from zope.interface import implements
from zope.component import getUtility, getMultiAdapter

from enpraxis.educommons.utilities.interfaces import IECUtility
from enpraxis.staticsite.utilities.staticsiteutility import StaticSiteUtility
from enpraxis.staticsite.utilities.interfaces import IStaticSiteUtility

class eduStaticSiteUtility(StaticSiteUtility):
    """ Deploy a static site """

    implements(IStaticSiteUtility)

    def runDocumentFilters(self, portal, current, soup, ssprops):
        self.filterBaseTag(soup, current)
        self.filterIgnoredSections(soup, ssprops)
        self.filterIgnoredPortlets(soup, ssprops)        
        self.filterIgnoredActions(soup, ssprops)
        self.filterCSSLinks(soup, current)
        self.filterIEFixesCSS(soup, current)
        self.filterS5BaseUrl(soup, current)     
        self.filterBaseFilesLinks(soup, current, portal, ssprops)           
        self.filterImageFullscreenBackLink(soup, current)
        self.filterCourseDownloadLink(soup, current, portal, ssprops)
        self.filterAttributionLinks(soup, current, portal, ssprops)
        self.filterCSSValidatorLink(soup, current, portal, ssprops)        
        self.filterBookmarkletsLinks(soup, current, portal, ssprops)
        links = self.getDocumentLinks(soup)
        for x in links:
            orig = x['href']
            x['href'] = self.filterDocumentLink(x['href'],
                                                current,
                                                portal,
                                                ssprops.getProperty('views_to_add'),
                                                ssprops.getProperty('non_html_views'))
            #print '   %s => %s' %(orig, x['href'])

        data = soup.prettify()
        return self.filterPortalUrl(data, current)

    def filterCourseDownloadLink(self, soup, current, portal, ssprops):
        link = soup.find('dd', id='download_course')
        if link:
            href = link.a['href']
            result = current
            hr = urlparse(current)
            p = urlparse(portal.portal_url())
            if p[1] == hr[1]:
                h = hr[2].split('/')
                if h[-1] == 'index.html':
                    h = h[:-1]
                for view in ssprops.getProperty('views_to_add'):
                    if view in h[-1]:
                        h[-1] = h[-1].replace('-%s.html' % view, '')                  
                result = portal.portal_catalog.searchResults(query={'path':'/'.join(h),}, id=h[-1])[0].getObject()
                course = getUtility(IECUtility).FindECParent(result)
                zip_url = '%s/%s.zip' % (course.absolute_url(), course.id)
                link.a['href'] = zip_url                
                
    def filterAttributionLinks(self, soup, current, portal, ssprops):
        if current == portal.portal_url():
            current += '/index.html'
        elif '.htm' not in current:
            current += '.html'
        ccite = soup.find(id='click_citation')
        pcite = soup.find(id='print_citation')
        scite = soup.find(id='skinless_citation')
        portal_url = portal.portal_url()
        deploy_url = ssprops.getProperty('deployment_url')
        if ccite:
            sstring = ccite['onclick']
            pattern = re.compile( r"\b(http:\/\/).*\b\." )
            nstring = pattern.sub('%s.' % current, sstring)
            nstring = nstring.replace(portal_url, deploy_url)
            ccite['onclick'] = nstring
        if pcite:
            sstring = pcite.contents[0]
            pattern = re.compile( r"\b(http:\/\/).*\b\." )
            nstring = pattern.sub('%s.' % current, sstring)
            nstring = nstring.replace(portal_url, deploy_url)
            pcite.contents[0].replaceWith(nstring)
        if scite:
            sstring = scite.span.contents[0]
            pattern = re.compile( r"\b(http:\/\/).*\b\." )
            nstring = pattern.sub('%s.' % current, sstring)
            nstring = nstring.replace(portal_url, deploy_url)
            scite.span.contents[0].replaceWith(nstring)
            
    def filterBookmarkletsLinks(self, soup, current, portal, ssprops):
        bookmarks = soup.find('span', id="toggledBookmarks")
        if bookmarks:
            links = bookmarks.findAll('a')
            for link in links:
                href = link['href']
                parts = href.split('=')
                index = 0
                for part in parts:
                    if portal.portal_url() in part:
                        url_parts = part.split('&')
                        if len(url_parts) > 0:
                            if '.htm' not in current:
                                current += '.html'
                            url_parts[0] = current
                            newurl = '&'.join(url_parts)
                        else:
                            newurl = current                                 
                        parts[index] = newurl
                    index += 1
                newurl = '='.join(parts)
                newurl = newurl.replace(portal.portal_url(), ssprops.getProperty('deployment_url'))
                link['href'] = newurl


