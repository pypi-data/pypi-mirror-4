Introduction
============

Package collective.gsa integrates Plone site with a Google Search Appliance (GSA). It
provides an indexing processor with collective.indexing as well as a search capabilities.

collective.gsa runs on Plone 4.x.

Installation
============
Add collective.gsa to your buildout.cfg to both eggs and create a part for the 
separate feeder startup script::

    [buildout]
    parts = gsafeeder

    eggs = collective.gsa

    [gsafeeder]
    recipe = zc.recipe.egg:scripts
    eggs = ${instance:eggs}
    arguments = 'gsa host:port', 'source', 'path_to_a_dir_with_generated_feeds', 'path_to_a_log_dir', 'pidfile'


After running
buildout and restarting the server, you can install it via Quick Installer either ZMI or 
Plone Add/Remove Products. After installing the package the GSA settings and GSA maintenance configlets
will appear in the Plone Control Panel. Follow the fields' description to set it up.

To start or stop the processing daemon run::
    
    ./bin/gsafeeder [start|stop|restart]

Global reindex
--------------
In the GSA maintenance configlet there is a tool to globally reindex the whole site. If the site is a large one, 
memory related issues may appear. Thus the reindex allows you to run it piece by piece by batching the objects.

If it is more suitable to run rather more small batches then there is an example script global_reindex.py in the example folder which
runs the batch reindexes repeatedly.

Indexing
========
A indexing subscriber is created and set upon IObjectEditedEvent, IObjectInitializedEvent, IActionSucceededEvent, IObjectRemovedEvent and create relevant xml feeds which are saved on a filesystem where the gsafeeder daemon should process them.

The package contains content providers for objects implementing IATDocument, IATFile and IATContentType. 
 * For document CTs (Page, News Items etc.) the default page is rendered.
 * For file CTs the primary file field is sent.
 * For other archetype based CTs the title and description.
 
To create support for other types just create your own content provider implementing interface IContentProvider 
and register it via zcml. For details look at the content_provider module and gsa's configure.zcml

The package supports dual indexing if you have two sites - e.g. secure for edit access and public for anonymous access.
The object's identifier in GSA is its url which is obtained using object's absolute_url method. 
Thus all the indexing has to be done from the url you want it to be indexed for ( e.i. not from localhost).
In the GSA's control panel you can set a dual base url for anonymous site. Then the url is constructed using the dual url plus 
absolute_url_path method.

When reindexing object, the feed id added to a persistent queue and is removed when successfully sent to GSA hence if GSA is 
unreachable the feed will be send when another object is reindexed.

Fact that GSA received the feed does not mean that it is going to be indexed ( e.i. the url is not in the Matched URLs settings )
If your objects are not indexed, please, check the GSA's Crawl and Index settings.

Searching
=========
This package replaces the search template and livesearch script to use GSA as a search engine. This is done by adding a gsasearch=on
into the search request to avoid using GSA search for internal searches ( such as navigation, folder contents etc. )

The plone's advanced search is at the default search_form template and does not use GSA at all, because GSA does not handle 
indexes as zope's ZCatalog does. However you can use the GSA's advanced search which url you can set at the local GSA control panel.

Uninstall
=========
To remove collective.gsa just uninstall it via QuickInstaller and remove it from buildout.


Current Status
==============

The basic implementation is nearly finished and we aim to write the neccessary tests for it.


Credit
======

This code was inspired by collective.solr package and it was kindly sponsored by 
University of Leicester.


