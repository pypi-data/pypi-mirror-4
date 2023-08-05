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

import Globals
from zope.interface import Interface
from zope.component import getUtility
from zope.schema import TextLine
from plone.app.form.base import AddForm
from Products.Five.browser import BrowserView
from zope.formlib.form import FormFields, action
from enpraxis.staticsite import StaticSiteMessageFactory as _
from enpraxis.staticsite.utilities.interfaces import IStaticSiteUtility

class IStaticSiteDeployForm(Interface):
    """ Interface for Static Site Deployment Form """


class StaticSiteDeployForm(AddForm):
    """ Stuff """

    form_fields = FormFields(IStaticSiteDeployForm)

    label = _(u'Deploy a Static Site')
    description = _(u'Deploy a static version of your Plone site.')

    def __init__(self, context, request):
        super(StaticSiteDeployForm, self).__init__(context, request)
        
    @action(_(u'Deploy'),
           name = u'Deploy')

    def action_deploy(self, action, data):
        """ Deploy a static site. """
        ssutil = getUtility(IStaticSiteUtility)
        ssutil.deploySite(self.context)
        self.request.response.redirect('deployed')
        
class DeployedView(BrowserView):        
    """ Stuff """
    
    def getDeploymentInformation(self, context):
        """ retrun the deployment path """
        ssprops = context.portal_url.portal_properties.staticsite_properties
        ssutil = getUtility(IStaticSiteUtility)
        return ssutil.getDeploymentPath(context), ssprops.deployment_url
        