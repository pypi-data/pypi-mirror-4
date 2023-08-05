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

import unittest
import Globals
from base import StaticSiteTestCase
from mocker import KWARGS, ARGS, ANY
from plone.mocktestcase import MockTestCase
from BeautifulSoup import BeautifulSoup
from Products.CMFPlone.tests.dummy  import Dummy
from enpraxis.staticsite.utilities.staticsiteutility import StaticSiteUtility
from enpraxis.staticsite.utilities.interfaces import IStaticSiteUtility
from zope.component import getUtility

test_links = """<a href="http://localhost:8080/site/front-page">front-page</a>
<a href="#TOP">Top</a>"""

class StaticSiteTest(StaticSiteTestCase):
    """ Test Static site product """

    def test_getDocumentLinks(self):
        """ Test method for finding links in documents """
        soup = BeautifulSoup(test_links)
        ssutil = getUtility(IStaticSiteUtility)
        links = ssutil.getDocumentLinks(soup)
        self.assertEqual(len(links), 2)
        self.assertEqual(links[0]['href'], 'http://localhost:8080/site/front-page')
        
    def test_filterDocumentLink(self):
        """ Test combined document filter functions """
        ssutil = getUtility(IStaticSiteUtility)
        link = ssutil.filterDocumentLink('#TOP', '', None, [], [])
        self.assertEqual(link, '#TOP')
        link = ssutil.filterDocumentLink('javascript:void(0);', '', None, [], [])
        self.assertEqual(link, 'javascript:void(0);')

    def test_convertLinkToAbsolute(self):
        """ test the convert to absolute link method """
        ssutil = getUtility(IStaticSiteUtility)
        link = ssutil._convertLinkToAbsolute(
            './hello',
            'http://localhost:8080/site')
        self.assertEqual(link, 'http://localhost:8080/site/hello')
        link = ssutil._convertLinkToAbsolute(
            '../hello',
            'http://localhost:8080/site/folder')
        self.assertEqual(link, 'http://localhost:8080/site/hello')
        link = ssutil._convertLinkToAbsolute(
            '../hello',
            'http://localhost:8080/site/Folder1/Folder2')
        self.assertEqual(link, 'http://localhost:8080/site/Folder1/hello')
        link = ssutil._convertLinkToAbsolute(
            '../Folder3/hello',
            'http://localhost:8080/site/Folder1/Folder2')
        self.assertEqual(link, 'http://localhost:8080/site/Folder1/Folder3/hello')
        link = ssutil._convertLinkToAbsolute(
            'http://localhost:8080/site/test',
            'http://localhost:8080/site/folder/page')
        self.assertEqual(link, 'http://localhost:8080/site/test')

    def test_convertObjectLink(self):
        """ test convert link via object type filter """
        portal = Dummy()
        pcat = Dummy()
        srd = Dummy()
        srd.is_folderish = False
        srd.Type = 'Page'
        
        pcat.searchResults = lambda query,id:[srd]
        portal.portal_catalog = pcat
        portal.portal_url = lambda :'http://localhost:8080/site'

        ssutil = getUtility(IStaticSiteUtility)
        link = ssutil._convertObjectLink('http://localhost:8080/site/front-page', portal, [], [])
        self.assertEqual(link, 'http://localhost:8080/site/front-page.html')
        link = ssutil._convertObjectLink('http://localhost:8080/site/front-page/presentation_view',
                                         portal,
                                         ['presentation_view'],
                                         [])
        self.assertEqual(link, 'http://localhost:8080/site/front-page-presentation_view.html')
        srd.is_folderish = True
        link = ssutil._convertObjectLink('http://localhost:8080/site/folder', portal, [], [])
        self.assertEqual(link, 'http://localhost:8080/site/folder/index.html')
        link = ssutil._convertObjectLink('http://localhost:8080/site/folder/rss', portal, ['rss'], [])
        self.assertEqual(link, 'http://localhost:8080/site/folder/index-rss.html')

    def test_convertLinkToRelative(self):
        """ Test the convert to relative method """
        ssutil = getUtility(IStaticSiteUtility)
        link = ssutil._convertLinkToRelative(
             'http://localhost:8080/site/',
             'http://localhost:8080/site/front-page')
        self.assertEqual(link, '')
        link = ssutil._convertLinkToRelative(
             'http://localhost:8080/site/',
             'http://localhost:8080/site/Folder/page.html')
        self.assertEqual(link, '../')
        link = ssutil._convertLinkToRelative(
             'http://localhost:8080/site/index.html',
             'http://localhost:8080/site/Folder1/page.html')
        self.assertEqual(link, '../index.html')        
        link = ssutil._convertLinkToRelative(
             'http://localhost:8080/site/Folder2/index.html',
             'http://localhost:8080/site/Folder1/page.html')
        self.assertEqual(link, '../Folder2/index.html')
        link = ssutil._convertLinkToRelative(
             'http://localhost:8080/site/Folder2/some_view',
             'http://localhost:8080/site/Folder2/page.html')
        self.assertEqual(link, 'some_view')

class TestStaticUtility(MockTestCase):
    """ Test methods within enpraxis.staticsite.utilities.staticutility.py """
    
    def test_deploySite(self):
        """ test the deploySite method """
        
    def test_traverse(self):
        """ test the traverse method """
        


    def test_deployObject(self):
        """ test the deployObject method """
        #purlfunc = lambda: 'http://localhost:8080/site'
        #dummy1  = self.create_dummy(portal_url = purlfunc, is_folderish = True, Type = ['page'])
        #ss_mock = self.mocker.proxy(StaticSiteUtility(u'testtype'))
        #self.expect(ss_mock._getObjPath(ARGS)).result('/test-folder/test-folder-1')
        #self.expect(ss_mock._createDirectory(ARGS)).result(None)
        #self.expect(ss_mock._httpget(ARGS)).result(None)
        #self.expect(ss_mock.runFilters(ARGS)).result(None)
        #self.mock_utility(ss_mock, IStaticSiteUtility, name=u'testtype')
        #self.mocker.replay()
        #ssutil = getUtility(IStaticSiteUtility, name = u'testtype')
        #ssutil.deployObject('http://localhost:8080/site', dummy1, 'test-folder/test-folder', 'http://www.plone.org')

#     def runTestUtility(self, dummy):
#         """ helper class for running utility """
#         ssutil = getUtility(IStaticSiteUtility, name = u'testtype')
#         ssutil.deployObject('http://localhost:8080/site', dummy, 'test-folder/test-folder', 'http://www.plone.org')
                
    def test_runFilters(self):
        """ test the runFilters method """

    def test_getDeploymentPath(self):
        """ test the _getDeploymentPath method """
        #Globals.BobobaseName = '/test-root/zope/dev/test/var/Data.fs'
        #ssu = StaticSiteUtility()
        #dspath = ssu._getDeploymentPath('test-path')
        #self.assertEqual(dspath, '/test-root/zope/dev/test/var/test-path')

    def test_getObjPath(self):
        """ test the _getObjPath method """
        
    def test_createDirectory(self):
        """ test the _createDirectory method """
        
    def test_httpget(self):
        """ test the _httpget method """

    def test_writeFile(self):
        """ the the _writeFile method """
        

def test_suite():
    """Test suite """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(StaticSiteTest))
    return suite
