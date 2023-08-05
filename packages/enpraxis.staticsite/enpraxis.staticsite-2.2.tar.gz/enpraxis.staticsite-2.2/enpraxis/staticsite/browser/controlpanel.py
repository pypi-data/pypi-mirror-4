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

from zope.interface import Interface, implements
from zope.component import adapts, getUtility
from zope.schema import TextLine, List, Tuple
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFPlone.utils import getToolByName
from plone.app.controlpanel.form import ControlPanelForm
from zope.formlib.form import FormFields

from enpraxis.staticsite import StaticSiteMessageFactory as _

class IStaticSiteSchema(Interface):
    """ Schema for static site configuration. """

    deployment_path = TextLine(title=_(u'Deployment Path'),
                               description=_(u'Path to the static site deployment.'),
                               required=True)

    deployment_url = TextLine(title=_(u'Deployment URL'),
                              description=_(u'Base URL to the static site deployment.'),
                              required=True)
    
    plone_sitemap = TextLine(title=_(u'Sitemap'),
                             description=_(u'The sitemap file.'),
                             required=True)

    google_file= TextLine(title=_(u'Google File'),
                          description=_(u'The google file.'),
                          required=True)

    base_files = List(title=_(u'Base Files'),
                      description=_(u'A list of basic site files and resources to download'),
                      required=True,
                      value_type=TextLine(),)
    
    css_images = List(title=_(u'CSS Images'),
                      description=_(u'A list of CSS images related to a custom theme'),
                      required=False,
                      value_type=TextLine(),)

    states_to_add = List(title=_(u'Add States'),
                         description=_(u'Add content that is currently in the following states'),
                         required=True,
                         value_type=TextLine(),)

    actions_to_ignore = List(title=_(u'Ignore Actions'),
                             description=_(u'Actions to be filtered out of content'),
                             required=True,
                             value_type=TextLine(),)
    
    sections_to_ignore = List(title=_(u'Ignore Document Sections'),
                              description=_(u'Document sections to be filtered out by CSS id tag'),
                              required=True,
                              value_type=TextLine(),)

    portlets_to_ignore = List(title=_(u'Ignore Portlets'),
                                description=_(u'Portlets to be filtered out by CSS class'),
                                required=True,
                                value_type=TextLine(),)
    
    views_to_add = List(title=_(u'Additional Views'),
                        description=_(u'Additional views that need to be stored'),
                        required=True,
                        value_type=TextLine(),)
    
    non_html_views = List(title=_(u'Non HTML Views'),
                          description=_(u'Views that are included but not based on HTML.'),
                          required=True,
                          value_type=TextLine(),)

class StaticSiteControlPanelAdapter(SchemaAdapterBase):
    """ Control panel adapter for static site product. """

    adapts(IPloneSiteRoot)
    implements(IStaticSiteSchema)

    def __init__(self, context):
        super(StaticSiteControlPanelAdapter, self).__init__(context)
        self.props = getUtility(IPropertiesTool)
        self.ssprops = self.props.staticsite_properties


    def _checkList(self, list):
        if len(list) == 1 and list[0] == '':
            return ()
        else:
            return list

    def get_deployment_path(self):
        return self.ssprops.getProperty('deployment_path')

    def set_deployment_path(self, dp):
        if not dp.endswith('/'):
            dp += '/'
        self.ssprops.manage_changeProperties(deployment_path=dp)

    def get_deployment_url(self):
        return self.ssprops.getProperty('deployment_url')

    def set_deployment_url(self, du):
        self.ssprops.manage_changeProperties(deployment_url=du)

    def get_plone_sitemap(self):
        return self.ssprops.getProperty('plone_sitemap')

    def set_plone_sitemap(self, sm):
        self.ssprops.manage_changeProperties('plone_sitemap')

    def get_google_file(self):
        return self.ssprops.getProperty('google_file')

    def set_google_file(self, gf):
        self.ssprops.manage_changeProperties(google_file=gf)

    def get_base_files(self):
        return self.ssprops.base_files

    def set_base_files(self, basefiles):
        self.ssprops.base_files = basefiles

    def get_css_images(self):            
        return self._checkList(self.ssprops.css_images)

    def set_css_images(self, cssimages):
        self.ssprops.css_images = cssimages

    def get_states_to_add(self):
        return self.ssprops.states_to_add

    def set_states_to_add(self, states):
        self.ssprops.states_to_add = states
        
    def get_actions_to_ignore(self):
        return self.ssprops.actions_to_ignore

    def set_actions_to_ignore(self, actions):
        self.ssprops.actions_to_ignore = actions

    def get_sections_to_ignore(self):
        return self.ssprops.sections_to_ignore

    def set_sections_to_ignore(self, sections):
        self.ssprops.sections_to_ignore = sections

    def get_portlets_to_ignore(self):
        return self.ssprops.portlets_to_ignore

    def set_portlets_to_ignore(self, portlets):
        self.ssprops.portlets_to_ignore = portlets

    def get_views_to_add(self):
        return self.ssprops.views_to_add

    def set_views_to_add(self, views):
        self.ssprops.views_to_add = views

    def get_non_html_views(self):
        return self.ssprops.non_html_views

    def set_non_html_views(self, views):
        self.ssprops.non_html_views = views

    deployment_path = property(get_deployment_path, set_deployment_path)
    deployment_url = property(get_deployment_url, set_deployment_url)    
    plone_sitemap = property(get_plone_sitemap, set_plone_sitemap)
    google_file = property(get_google_file, set_google_file)
    base_files = property(get_base_files, set_base_files)        
    css_images = property(get_css_images, set_css_images)            
    states_to_add = property(get_states_to_add, set_states_to_add)        
    actions_to_ignore = property(get_actions_to_ignore, set_actions_to_ignore)
    sections_to_ignore = property(get_sections_to_ignore, set_sections_to_ignore)
    portlets_to_ignore = property(get_portlets_to_ignore, set_portlets_to_ignore)    
    views_to_add = property(get_views_to_add, set_views_to_add)
    non_html_views = property(get_non_html_views, set_non_html_views)

class StaticSiteControlPanel(ControlPanelForm):

    form_fields = FormFields(IStaticSiteSchema)

    label = _(u'Static Site Settings')
    description = _(u'Settings which control static site deployment.')
    form_name = _(u'Static Site Settings')
