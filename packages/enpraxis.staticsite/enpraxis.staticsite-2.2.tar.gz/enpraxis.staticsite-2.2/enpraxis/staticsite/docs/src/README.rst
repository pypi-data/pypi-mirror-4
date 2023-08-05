StaticSite Utility
===================

StaticSite is a Plone Add-on designed to deploy a static version of your plone site to the filesystem.  There are many configuration options available for StaticSite, which should be reviewed before deploying a static site.

Control Panel
-------------

The StaticSite control panel is available for the Site Setup link, underneath the Add-on Product Configuration

.. image:: images/site_setup.png
   :alt: StaticSite Add-on Product Configuration

Deployment Path and URL
-----------------------

.. image:: images/deployment.png
   :alt: Deployment Path and URL

The *Deployment Path* defines the root folder on the filesystem to which files will be written. The base folder will always be defined by where the Data.fs is stored within your instance.  The *Deployment Path* is appended to that path.

For instance:

  Data.fs path :: /path/to/your/instance/var/Data.fs

  Static Site path :: /path/to/your/instance/var/static

The *Deployment URL* defines the base url for the static site. You will need to configure Apache accordingly. This value is utilized in the document filters, which rewrite relative and absolute paths appropriately.

Base Files
----------

*Base Files* are typically resources that are acquired by acquisition in Plone.  These resources are written to the root of your static site deployment, and referenced accordingly.  You may add and remove *Base Files* as needed.

.. image:: images/base1.png
   :alt: Base Files

.. image:: images/base2.png
	 :alt: Base Files

CSS Images
----------

*CSS Images* are images utilized in customized themes. These images are written to the deployment path of the CSS resources on the filesystem.  If you are utilizing anything but a custom logo, you must add the files to the *CSS Images* field.

.. image:: images/css.png
   :alt: CSS Images

Add States
----------

By default, only content in the *published* state is deployed to the filesystem.  If your instance utilizes other states that are visible to the public, you may add that state to the *Add States* field.

.. image:: images/states.png
   :alt: Add States

Ignored Actions and Document Sections
-------------------------------------

Static site deploys a version to the filesystem that is purely .html driven.  Therefore, certain sections and actions that are driven by dynamic functionality must be removed from each deployed page.  

.. image:: images/ignored.png
   :alt: Ignored Actions and Document Sections

Ignored Portlets
-------------------------------------

Many portlets rely on dynamic content/interactivity. Static site will extract portlets defined below.

.. image:: images/portlets.png
   :alt: Ignored Portlets

Additional Views and Non HTML views
-----------------------------------

*Additional Views* can be defined for:

* 'single-object-like' views - accessibility-info, for example
* views over content objects - presentation_view, for example

For views that are not based on HTML, you may define them as *Non HTML Views*. This will allow XML and other non-html views to be deployed properly.

.. image:: images/views.png
   :alt: Views

Extending Functionality
=======================

If you do choose to add additional views, you will likely need to extend the functionality of the utility to account for these views. You may do this by customizing the default code, or overwriting the utility in a separate product::

    <utility
        provides="enpraxis.staticsite.utilities.interfaces.IStaticSiteUtility"
        factory=".utilities.staticsiteutility.eduStaticSiteUtility"
    />


The filtering mechanism utilizes BeautifulSoup_ to parse the HTML of each static object. Typically, additionally filters will be added to runDocumentFilters to account for additional/custom views. For example, the Add-on product PloneBookmarklets renders links that must be dealt with differently than other document actions:

.. _BeautifulSoup: http://www.crummy.com/software/BeautifulSoup/documentation.html

::

  class eduStaticSiteUtility(StaticSiteUtility):
	    """ Deploy a static site """

	    implements(IStaticSiteUtility)

	    def runDocumentFilters(self, portal, current, soup, ssprops):
	        self.filterBaseTag(soup, current)
	        ...
	        ...
	        self.filterBookmarkletsLinks(soup, current, portal, ssprops)
          ...

      ...
      ...

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

Deploying a Static Site
=======================

To deploy a static version of your plone instance, navigate to the *deploy* action in the upper right hand corner.

.. image:: images/deploy.png
   :alt: Deploy Static Site

Press the *Deploy Site* button to being the process of generating a static site.  Be patient, as this may take quite some time for large instances.

.. image:: images/deploy2.png
   :alt: Deploy Static Site


	