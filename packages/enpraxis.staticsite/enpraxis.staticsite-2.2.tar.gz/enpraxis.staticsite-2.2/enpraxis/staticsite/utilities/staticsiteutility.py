##################################################################################
#    Copyright (c) 2009 Massachusetts Institute of Technology, All rights reserved.
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
##################################################################################

__author__ = '''Brent Lambert, David Ray, Jon Thomas'''
__version__ = '$ Revision 0.0 $'[11:-2]

import os
import re
import string
import Globals
from BeautifulSoup import BeautifulSoup
from mimetypes import guess_type
from os import makedirs as os_makedirs
from os.path import join as os_join
from os.path import lexists as os_lexists
from os.path import split as os_split

from urllib2 import urlopen
from urllib2 import HTTPError
from urlparse import urlparse, urlunparse
from Products.PythonScripts.standard import url_quote

from OFS.SimpleItem import SimpleItem
from zope.interface import implements
from interfaces import IStaticSiteUtility
from zope.component import getUtility, getMultiAdapter

class StaticSiteUtility(SimpleItem):
    """ Deploy a static site """

    implements(IStaticSiteUtility)


    def deploySite(self, context):
        """ Deploy the site """
        ssprops = context.portal_url.portal_properties.staticsite_properties
        dpath = self._getDeploymentPath(ssprops.getProperty('deployment_path'))
        # Deploy default objects
        self.deploySiteStructure(context, ssprops, dpath)
        # Deploy site object
        self.deployObject(context.absolute_url(), context, context.Type(), dpath, ssprops, True)
        # Deploy objects based on catalog search
        brains = context.portal_catalog.searchResults(
            path={'query':'/'.join(context.getPhysicalPath()),
                  'depth':1,},
            review_state=ssprops.getProperty('states_to_add'))
        for brain in brains:
            self.deployObject(brain.getURL(),
                              context,
                              brain.Type,
                              dpath,
                              ssprops,
                              folderish=brain.is_folderish)
            self.traverse(brain, dpath, ssprops)


    def deploySiteStructure(self, context, ssprops, dpath):
        """ Get the base framework and resources needed to build the chrome locally  """
        portal_url = context.portal_url()
        portal_catalog = context.portal_catalog
        url = urlparse(portal_url)
        urlpath = url[2].split('/')

        # Deploy base files that are used sitewide in the chrome
        for x in ssprops.getProperty('base_files'):
            objurl = urlunparse((url[0], url[1], '/'.join(urlpath + [x]), url[3], url[4], url[5]))
            #path = self._getObjPath(objurl, portal_url, dpath)
            raw = self._httpget(objurl)
            ftype = guess_type(x)[0]
            if ftype is None:
                path = self._getObjPath(objurl, portal_url, dpath)                
                self._writeFile(path, raw)                
            elif 'css' in ftype:
                path = self._getObjPath(objurl, portal_url, dpath + 'css/')
                self._writeFile(path, raw)
            elif 'javascript' in ftype:
                path = self._getObjPath(objurl, portal_url, dpath + 'js/')                
                self._writeFile(path, raw)
            elif 'image' in ftype:
                path = self._getObjPath(objurl, portal_url, dpath + 'images/')
                self._writeFile(path, raw, True)
            else:
                path = self._getObjPath(objurl, portal_url, dpath)                
                self._writeFile(path, raw)
                
        # Deploy Current Theme CSS
        cssreg = context.portal_css
        cssurl = cssreg.absolute_url()
        skinname = context.getCurrentSkinName()
        for x in cssreg.getEvaluatedResources(context):
            if x.getRendering() != 'inline':
                surl = '%s/%s/%s' %(cssurl, skinname, x.getId())
                path = self._getObjPath(surl, portal_url, dpath)
                surl = '%s/%s/%s' %(cssurl, url_quote(skinname), x.getId())
                raw = self._httpget(surl)
                self._writeFile(path, raw)

        # Deploy Current Theme CSS Images into the appropriate skin folder
        css_images = ssprops.getProperty('css_images')
        if len(css_images) > 0:            
            for x in css_images:   
                if x != '':            
                    iurl = '%s/%s' %(portal_url, x)
                    surl = '%s/%s/%s' %(cssurl, skinname, x)
                    path = self._getObjPath(surl, portal_url, dpath)
                    raw = self._httpget(iurl)
                    self._writeFile(path, raw)
                    
        # Deploy Javascript
        jsreg = context.portal_javascripts
        jsurl = jsreg.absolute_url()
        for x in jsreg.getEvaluatedResources(context):
            if x.getInline() != True:            
                surl = '%s/%s/%s' %(jsurl, skinname, x.getId())
                path = self._getObjPath(surl, portal_url, dpath)
                surl = '%s/%s/%s' %(jsurl, url_quote(skinname), x.getId())
                raw = self._httpget(surl)
                self._writeFile(path, raw)    

        # Deploy site actions
        site_actions = context.portal_actions.site_actions.listActions()
        for x in site_actions:
            if x.id not in ssprops.getProperty('actions_to_ignore') and x.visible == True:
                action_url = x.url_expr.split('/')[-1]
                url = '%s/%s' % (portal_url, action_url)
                path = self._getObjPath(url, portal_url, dpath)
                path += '.html'
                raw = self._httpget(url)        
                self._writeFile(path, raw)
        
    def traverse(self, brain, dpath, ssprops):
        """ Traverse the site. """
        brains = brain.portal_catalog.searchResults(
            path={'query':brain.getPath(), 'depth':1},
                  review_state=ssprops.getProperty('states_to_add'))
        for br in brains:
            self.deployObject(br.getURL(),
                              br.portal_url,
                              br.Type,
                              dpath,
                              ssprops,
                              folderish=br.is_folderish)
            if br.is_folderish:
                self.traverse(br, dpath, ssprops)
            
    def deployObject(self, url, portal, ctype, dpath, ssprops, folderish=False, hastext=False):
        """ Deploy an object """
        path = self._getObjPath(url, portal.portal_url(), dpath)
        if folderish:
            # print '@@@ '+  url + '/index.html'
            self.processDocument(url, portal, dpath, ssprops, True)
        elif ctype in ['Page']:
            # Fix this so that it deals with the case where you have both a file and a file.html in the
            # same folder
            # print '*** '+  url
            self.processDocument(url, portal, dpath, ssprops)
        else:
            # Write the object to the filesystem
            raw = self._httpget(url) 
            self._writeFile(path, raw, True)
            # Process the view of the object
            aurl = urlparse(url)
            aurl = urlunparse((aurl[0], aurl[1], aurl[2] + '-view.html', aurl[3], aurl[4], aurl[5]))
            # print 'vvv '+  aurl
            self.processDocument(url + '/view', portal, dpath, ssprops, alturl=aurl)
            # If it is an image process the fullscreen view
            if ctype in ['Image']:
                aurl = urlparse(url)
                aurl = urlunparse((aurl[0], aurl[1], aurl[2] + '-image_view_fullscreen.html', aurl[3], aurl[4], aurl[5]))
                # print 'iii '+  aurl
                self.processDocument(url + '/image_view_fullscreen', portal, dpath, ssprops, alturl=aurl)


    def _getDeploymentPath(self, sp):
        """ Get the default static path location. """
        dpath = os_split(Globals.BobobaseName)[0]
        return os_join(dpath, sp)
        
    def _getObjPath(self, url, portal_url, dpath):
        """ Get the object path based on the deployment path. """
        if portal_url + '/' in url:
            objpath = url.replace(portal_url + '/', '')
        else:
            objpath = url.replace(portal_url, '')
        path = dpath
        for x in objpath.split('/'):
            path = os_join(path, x)
        return path
    
    def _createDirectory(self, path):
        """ Create a directory on the filesystem """      
        if not os_lexists(path):
            os_makedirs(path)
            
    def _httpget(self, url):
        """ Get html for the url """
        try:
            f = urlopen(url)
            data = f.read()
            f.close()
            return data
        except HTTPError, e:           
            # print '!!! Error : %s %s for url: %s' % (e.code, e.msg, e.filename)
            return ''
            
    def _writeFile(self, fn, data, binary=False):
        self._createDirectory(os_split(fn)[0])
        if binary:
		    f = open(fn, 'wb')
        else:
            f = open(fn, 'w')
        f.write(data)
        f.close()
    
    def processDocument(self, url, portal, dpath, ssprops, isFolderish=False, alturl=None):
        if alturl:
            aurl = alturl
        else:
            aurl = url
        path = self._getObjPath(aurl, portal.portal_url(), dpath)
        raw = self._httpget(url)
        soup = BeautifulSoup(raw)
        self.deployDocumentActions(portal, aurl, dpath, soup, ssprops)
        self.deployPresentationView(portal, aurl, dpath, soup, ssprops)        
        self.deployNonActionNonHTMLViews(portal, aurl, dpath, soup, ssprops)
        if isFolderish:
            curl = aurl + '/index.html'
        else:
            curl = aurl
        body = self.runDocumentFilters(portal, curl, soup, ssprops)
        mpath = path
        if isFolderish:
            mpath += '/index.html'
        elif '.htm' not in mpath:
            mpath += '.html'
        self._writeFile(mpath, body)


    def deployPresentationView(self, portal, current, dpath, soup, ssprops):
        #Look for presentation view
        raw_pres = soup.find('p', id='link-presentation')
        if raw_pres:
            url = raw_pres.a['href']
            upath = urlparse(url)
            p = upath[2].split('/')
            obj = p[:-1]
            view = p[-1]
            if view in ssprops.getProperty('views_to_add'):
                mpath = self._getObjPath(url, portal.portal_url(), dpath)
                mpath = os.path.split(mpath)
                raw = self._httpget(url)
                asoup = BeautifulSoup(raw)
                body = self.runDocumentFilters(portal, current, asoup, ssprops)
                results = portal.portal_catalog.searchResults(
                    query={'path':'/'.join(obj[:-1]),},
                    id=obj[-1])
                if results:
                    if results[0].is_folderish:
                        mpath = '%s/index-%s' %(mpath[0], mpath[1])
                    else:
                        mpath = '%s-%s' %(mpath[0], mpath[1])
                    if  view not in ssprops.getProperty('non_html_views'):
                        mpath += '.html'
                    self._writeFile(mpath, body)            
            

    def deployDocumentActions(self, portal, current, dpath, soup, ssprops):
        # Look for document actions
        raw_da = soup.find('div', {'class':'documentActions'})
        if raw_da:
            # Step through document actions and see if they are in the soup
            da = portal.portal_actions.document_actions.listActions()
            for x in da:
                # If we are not ignoring the action
                if x.id not in ssprops.getProperty('actions_to_ignore'):
                    # Find the action in the soup
                    act = raw_da.find('li', id='document-action-%s' %x.id)
                    if act:
                        link = act.find('a')
                        if link and link.has_key('href'):
                            # Process the action
                            url = link['href']
                            upath = urlparse(link['href'])
                            p = upath[2].split('/')
                            obj = p[:-1]
                            view = p[-1]
                            # If we are going to add the action, process it
                            if view in ssprops.getProperty('views_to_add'):
                                mpath = self._getObjPath(url, portal.portal_url(), dpath)
                                mpath = os.path.split(mpath)
                                raw = self._httpget(url)
                                asoup = BeautifulSoup(raw)
                                body = self.runDocumentFilters(portal, current, asoup, ssprops)
                                results = portal.portal_catalog.searchResults(
                                    query={'path':'/'.join(obj[:-1]),},
                                    id=obj[-1])
                                if results:
                                    if results[0].is_folderish:
                                        mpath = '%s/index-%s' %(mpath[0], mpath[1])
                                    else:
                                        mpath = '%s-%s' %(mpath[0], mpath[1])
                                    if  view not in ssprops.getProperty('non_html_views'):
                                        mpath += '.html'
                                    self._writeFile(mpath, body)

    def deployNonActionNonHTMLViews(self, portal, aurl, dpath, soup, ssprops):
        #deploy non-html views that are not tied to views_to_add and not found as links within pages
        views_to_add = ssprops.getProperty('views_to_add')
        non_html_views = ssprops.getProperty('non_html_views')
        views = [x for x in non_html_views if x not in views_to_add]
        for view in views:
            if view == 'rdf':
                url = '%s/%s' % (aurl, view)
                raw = self._httpget(url)
                if len(raw) > 0:
                    raw = '<?xml version="1.0" encoding="utf-8" ?>\n' + raw
                    if '.htm' in aurl:
                        parts = aurl.split('.htm')
                        url = '%s.rdf' % parts[0] 
                    else:
                        url = url.replace('/rdf', '.rdf')
                    obj_path = url.replace(portal.portal_url()+'/', '')
                    dpath += '%s' % obj_path
                    self._writeFile(dpath, raw)

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
        self.filterCSSValidatorLink(soup, current, portal, ssprops)
        links = self.getDocumentLinks(soup)
        for x in links:
            orig = x['href']
            x['href'] = self.filterDocumentLink(x['href'],
                                                current,
                                                portal,
                                                ssprops.getProperty('views_to_add'),
                                                ssprops.getProperty('non_html_views'))
            # print '   %s => %s' %(orig, x['href'])
        data = soup.prettify()
        return self.filterPortalUrl(data, current)

    def filterBaseTag(self, soup, current):
        base = soup.findAll('base')
        for x in base:
            if x.has_key('href'):
                url = x['href']
                url = url.split(');')[0]
                url = self._convertLinkToRelative(url, current)
                x['href'] = url                

    def filterIgnoredActions(self, soup, ssprops):
        ftags = soup.findAll('div') + soup.findAll('li')
        for x in ftags:
            if x.has_key('id'):
                id = x['id']
                if 'document-action' in id:
                    act = id.split('-')[-1]
                    if act in ssprops.getProperty('actions_to_ignore'):
                        x.extract()

    def filterIgnoredSections(self, soup, ssprops):
        for x in ssprops.getProperty('sections_to_ignore'):
            tag = soup.find(id=x)
            if tag:
                if x == 'portal-personaltools':
                    tag.contents[1].replaceWith('<li>&nbsp;</li>')
                else:
                    tag.extract()
                
    def filterIgnoredPortlets(self, soup, ssprops):
        for x in ssprops.getProperty('portlets_to_ignore'):                    
            tag = soup.find('dl', {'class': 'portlet %s' % x})
            if tag:
                portlet = tag.parent
                column_wrapper = portlet.parent                
                portlet.extract()
                # Check for additional portlets in column, remove col if none
                if not 'portletWrapper' in column_wrapper.renderContents():
                    column_wrapper.parent.extract()
                
    def filterCSSLinks(self, soup, current):
        #There are 2 cases, importing stylesheets, and linked stylesheets
        styles = soup.findAll('style', type="text/css")
        for x in styles:
            body = x.contents[0]
            if '@import' in body:
                url = body.split('url(')[-1]
                url = url.split(');')[0]
                url = self._convertLinkToRelative(url, current)
                x.contents[0].replaceWith('<!-- @import url(%s); -->' %url)         
        styles = soup.findAll('link', type="text/css")
        for x in styles:
            if '.htm' not in current:
                current += '/index.html'
            if x.has_key('href'):
                url = x['href']
                url = self._convertLinkToRelative(url, current)
                x['href'] = url


    def filterIEFixesCSS(self, soup, current):
        ie_css = soup.find(text=re.compile("IEFixes.css"))
        if ie_css:
            url = ie_css.split('url(')[-1]
            url = url.split(');')[0]
            url.replace('IEFixes.css', 'css/IEFixes.css')
            nurl = self._convertLinkToRelative(url, current)
            ie_css.replaceWith('''<!--[if IE]>
                                  <style type="text/css" media="all">@import url(%s);</style>
                                  <![endif]-->''' %nurl)        

    def filterS5BaseUrl(self, soup, current):
        scripts = soup.findAll('script', type="text/javascript")
        for x in scripts:
            if len(x.contents) > 0 and 'base' in x.contents[0]:
                base_url = x.contents[0].split('url="')[-1]
                base_url = base_url.split('";')[0]
                if '.htm' not in base_url:
                    base_url += '.html'
                url = self._convertLinkToRelative(base_url, current)
                x.contents[0].replaceWith('var base_url="%s";' % url)

    def filterCSSValidatorLink(self, soup, current, portal, ssprops):
        for link in soup('a', {'href' : re.compile('css-validator')}):
            deployment_url = ssprops.getProperty('deployment_url')
            portal_url = portal.portal_url()
            url = link['href']
            url = url.split('uri=')[-1]
            url = url.split('%2F')[0]
            if '.htm' not in current:
                current += '.html'
            nurl = current.replace(portal_url, deployment_url)
            link['href'] = link['href'].replace(url, nurl)
        
    def filterImageFullscreenBackLink(self, soup, current):
        if 'image_view_fullscreen' in current:
            back = soup.find('a')
            if back:
                lt = back.find('span')
                if lt:
                    lt.contents[0].replaceWith('Back to Image')
                if back.has_key('href'):
                    back['href'] = current.replace('image_view_fullscreen.html', 'view.html')

    def filterBaseFilesLinks(self, soup, current, portal, ssprops):
        portal_url = portal.portal_url()
        for x in ssprops.getProperty('base_files'):
            ftype = guess_type(x)[0]
            if ftype is None:
                pass
            elif 'css' in ftype:
                tags = soup.findAll('link', {'href' : re.compile(x)})
                for tag in tags:
                    if portal_url in tag['href'] or len(tag['href'].split('/')) == 1:                    
                        abs_link = self._convertLinkToAbsolute(tag['href'], portal_url)
                        rel_link = self._convertLinkToRelative(abs_link, current)
                    else:
                        rel_link = tag['href']                        
                    tag['href']  = rel_link.replace(x, 'css/%s' % x) 
            elif 'javascript' in ftype:              
                tags = soup.findAll('script', {'src' : re.compile(x)})
                for tag in tags:
                    if portal_url in tag['src'] or len(tag['src'].split('/')) == 1:
                        abs_link = self._convertLinkToAbsolute(tag['src'], portal_url)
                        rel_link = self._convertLinkToRelative(abs_link, current)                    
                    else:
                        rel_link = tag['src']                        
                    tag['src']  = rel_link.replace(x, 'js/%s' % x)  
            elif 'image' in ftype:
                tags = soup.findAll('img', {'src' : re.compile(x)})
                for tag in tags:
                    if portal_url in tag['src'] or len(tag['src'].split('/')) == 1:
                        abs_link = self._convertLinkToAbsolute(tag['src'], portal_url)                    
                        rel_link = self._convertLinkToRelative(abs_link, current)                    
                    else:
                        rel_link = tag['src']
                    tag['src']  = rel_link.replace(x, 'images/%s' % x)

    def getDocumentLinks(self, soup):
        tags = soup.findAll('a') + soup.findAll('link')
        links = []
        for tag in tags:
            if tag.has_key('href'):
                url = urlparse(tag['href'])
                if not url[1] or 'localhost' in url[1]:
                    links.append(tag)
        return links

    def filterDocumentLink(self, link, current, portal, views, nviews):        
        lnk = link
        url = urlparse(lnk)
        if url[2] and 'javascript' != url[0]:
            lnk = self._convertLinkToAbsolute(lnk, current)
            lnk = self._convertObjectLink(lnk, portal, views, nviews)
            lnk = self._convertLinkToRelative(lnk, current)
        return lnk

    def _convertLinkToAbsolute(self, link, current):
        result = link
        c = urlparse(current)
        hr = urlparse(link)
        if not hr[0] and not hr[1]:
            cp = c[2].split('/')
            hp = hr[2].split('/')
            p = []
            for y in hp:
                if '.' == y:
                    pass
                elif '..' == y:
                    cp = cp[:-1]
                else:
                    p.append(y)
            result = urlunparse((c[0], c[1], '/'.join(cp + p), hr[3], hr[4], hr[5]))
        return result

    def _convertObjectLink(self, link, portal, views, nviews):
        # This only works for absolute links
        result = link
        hr = urlparse(link)
        p = urlparse(portal.portal_url())
        if p[1] == hr[1]:
            h = hr[2].split('/')
            view = ''
            if h[-1] in views:
                view = h[-1]
                h = h[:-1]
            results = portal.portal_catalog.searchResults(query={'path':'/'.join(h),}, id=h[-1])
            if results:
                path = ''
                if results[0].is_folderish:
                    if view:
                        path = '/'.join(h) + '/index' + '-%s' %view
                    else:
                        path = '/'.join(h) + '/index.html'
                else:
                    if view:
                        path = '/'.join(h) + '-%s' %view
                    elif h:
                        path = '/'.join(h)
                        if 'Page' == results[0].Type and '.htm' not in path:
                            path += '.html'
                if view and view not in nviews:
                    path += '.html'
                result = urlunparse((hr[0], hr[1], path, hr[3], hr[4], hr[5]))
            elif link == portal.portal_url():
                # Link points to site root
                result = urlunparse((hr[0], hr[1], '/'.join(h) + '/index.html', hr[3], hr[4], hr[5]))
        return result

    def _convertLinkToRelative(self, link, current):
        # This will break if the last item in the url path is a folder
        # Make sure you rewrite the link path before you call this function
        hr = urlparse(link)
        c = urlparse(current)
        if c[1] == hr[1]:
            url1 = c[2].split('/')
            url2 = hr[2].split('/')
            index = 0
            while url1[index:] and url2[index:] and url1[index] == url2[index]:
                index += 1
            p = []
            for y in range(len(url1[index+1:])):
                p.append('..')
            p = p + url2[index:]
            return urlunparse(('', '', '/'.join(p), hr[3], hr[4], hr[5]))
        

    def filterPortalUrl(self, data, current):
        """ Blanket filter to replace any remaining portal urls in the page. """
        return data.replace(current, '')
        

    def getDeploymentPath(self, context):
        ssprops = context.portal_url.portal_properties.staticsite_properties
        dpath = self._getDeploymentPath(ssprops.getProperty('deployment_path'))
        return dpath
        
        
