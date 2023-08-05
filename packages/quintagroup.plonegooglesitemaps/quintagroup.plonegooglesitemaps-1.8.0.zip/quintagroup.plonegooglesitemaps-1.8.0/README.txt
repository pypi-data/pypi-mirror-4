Introduction
============

Plone Google Sitemaps product allows Plone websites to get better visibility on Google search engine
by providing it with a complete listing of content URLs to website.

.. figure:: http://quintagroup.com/services/plone-development/products/google-sitemaps/plone-google-sitemaps.png

Plone Google Sitemaps allows you to enable different kinds of Google Sitemaps on your Plone website. 
Such Sitemaps help Google identify site URLs and the data under each site section. With Google Sitemaps
enabled, search engines could track your Plone site URLs faster and more efficiently, optimizing their 
search by placing all the information on one page.

With Plone Google Sitemaps product you can enable following Sitemap types on your Plone website:

* ``Content Sitemap`` - is a regular list of pages on your website. Creating and submitting such a Sitemap 
  lets Google know about all the pages on your Plone website, including URLs that may not be discoverable
  by Google's normal crawling process.
* ``Mobile Sitemap`` - is a specific type of Sitemap, that indexes all site URLs that serve mobile-oriented content.
* ``News Sitemap`` - is different from regular Sitemaps, since it is specific to Google News only.
  It uses the Sitemap protocol, with additional News-specific tags, defined by Google. The package brings protocol with 
  additional Google Sitemaps tab to News Item content type for defining NewsSitemap-specific meta tags. 

Different Sitemap types index their own content and do not depend on other Sitemaps. 

Usage
-----

To enable Google Sitemaps on your site:

* Add Sitemap(s) at Google Sitemap "Settings" tab (Add-on Products Configuarion -> Google Sitemaps). 
  You can add any of the Sitemap types: content, mobile or news. 
* Let Google know about your Sitemap(s) by adding your Sitemap to Google Sitemaps.

See detailed instructions on Plone Google Sitemaps usage at http://projects.quintagroup.com/products/wiki/qPloneGoogleSitemaps

MIGRATION
=========

If you UPGRADE an older version of quintagroup.plonegooglesitemaps package to a newer one:
------------------------------------------------------------------------------------------

* In your zope instance configuration or buildout replace old package version with a new one.
* Run plone instance and reinstall package with Quickinstaller tool ("Add-on Products" in plone control panel).

If you MIGRATE from Products.qPloneGoogleSitemaps to quintagroup.plonegooglesitemaps:
-------------------------------------------------------------------------------------
    
* Add to a new Plone instance/buildout both qPloneGoogleSitemaps product and last version quintagroup.plonegooglesitemaps package.
* Copy Data.fs from old Plone instance to new one.
* Start your new Zope instance/buildout.

The following steps are performed in the plone instance:

* With portal_migration (ZMI) - upgrade plone instance.
* With Quickinstaller tool ("Add-on Products" in plone control panel) deinstall old "Plone Google Sitemaps" product and install new version.
* Go to *Import* tab in portal_setup tool (ZMI), select "Migrate from qPloneGoogleSitemaps to quintagroup.plonegooglesitemaps" profile from selection box and choose same-named import step and push "Import selected steps" button.

And the last clean-up step:

* Remove qPloneGoogleSitemaps product from your zope instance/buildout configuration.

Screencast
----------

Watch Plone Google Sitemaps Screencasts at http://quintagroup.com/cms/screencasts/qplonegooglesitemaps to see how to use this products
on your Plone instance. Learn about how to install and configure Sitemaps on your Plone instance, how to create new Google Sitemaps, 
and how to let Google know about them.
  
Installation
------------

See http://projects.quintagroup.com/products/wiki/qPloneGoogleSitemaps/install
  
Requirements
------------

* Plone 4.1
* Plone 4.0
* Plone 3.1+

Links
-----

* See "Google Sitemaps": https://www.google.com/webmasters/sitemaps website for more information.
* Product Homepage: http://quintagroup.com/services/plone-development/products/google-sitemaps
* Documentation Area: http://projects.quintagroup.com/products/wiki/qPloneGoogleSitemaps
* Repository: http://svn.quintagroup.com/products/quintagroup.plonegooglesitemaps
* Releases: http://plone.org/products/qplonegooglesitemaps/releases
* Watch "Plone Google Sitemeps" Screencast at http://quintagroup.com/cms/screencasts/qplonegooglesitemaps

Authors
-------

* Myroslav Opyr
* Andriy Mylenkyi
* Nazar Ilchuk 
* Mykola Kharechko
* Vitaliy Stepanov

