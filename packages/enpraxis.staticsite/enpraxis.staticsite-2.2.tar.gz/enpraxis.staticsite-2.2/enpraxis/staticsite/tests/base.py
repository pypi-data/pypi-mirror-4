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

from zope.testing import doctest
from Products.PloneTestCase.PloneTestCase import setupPloneSite, PloneTestCase, FunctionalTestCase
from Products.PloneTestCase.layer import onsetup
from Products.Five import fiveconfigure, zcml
from Testing import ZopeTestCase as ztc

@onsetup
def setup_static_site_project():
    """
    Load and install packages required for enpraxis.staticsite tests
    """

    fiveconfigure.debug_mode = True
    import enpraxis.staticsite
    zcml.load_config('configure.zcml', enpraxis.staticsite)
    fiveconfigure.debug_mode = False
    ztc.installPackage('enpraxis.staticsite')

setup_static_site_project()
setupPloneSite(extension_profiles=['enpraxis.staticsite:default'])

oflags = (doctest.ELLIPSIS |
          doctest.NORMALIZE_WHITESPACE)

prod = 'enpraxis.staticsite'

class StaticSiteTestCase(PloneTestCase):
    """ Test class """

class StaticSiteFunctionalTestCase(FunctionalTestCase, StaticSiteTestCase):
    """ Functional test class """
