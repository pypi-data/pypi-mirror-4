ContentMigrator
===============

Ed Crewe, ILRT University of Bristol 2011

Please also see the README.txt for the containing egg ilrt.contentmigrator 

Install
-------

The exporter is contained in a Product designed for use in old plone, ie before 3, 
(and possibly plain zope) sites.
It exports the content into a plone3 style generic setup structure folder.

Simply drop the ContentMigrator folder into the Products directory in your old plone site. 

For the new plone site it can be installed in the normal manner as the ilrt.contentmigrator
egg in the buildout.

Concept
-------

From Andreas Jung's idea
http://www.zopyx.com/blog/when-the-plone-migration-fails-doing-content-migration-only
This conforms to the properties style of generic setup.

Exports content and replicates the folder structure of plone to a zope/var/structure 
folder on the file system.

Content gets default dublin core and workflow metadata in properties files
e.g. word.doc is exported with a separate word.doc.properties file. Whilst HTML document
content and archetypes have the properties packaged in the header of the file. 
The properties format uses the RFC822 mail format standard, which is the plone3 default 
for content marshalling, available by adding manage_FTPget to a content item url.

If archetypes are found their schema data is added to the properties.

XML optional format
-------------------

The RFC822 basic textual format for properties is the default format for zope generic setup 
content import, but for export to other CMS or systems XML is more standard hence 
there is an option to write all the properties info and textual content as XML. 

TODO
====

Zope content
------------

Add a means to export from plain zope sites, by adding form text boxes to specify header and 
footer text or regular expressions for stripping out from documents. Plus check any 
assumptions about workflow existing, etc. are suitably handled, and test with plain zope.

CMIS standard XML
-----------------

see http://docs.oasis-open.org/ns/cmis/core/200908/

Currently the XML export option just uses the Plone based field names as properties
it may be useful to add an optional filter to comply with the CMIS standard for the XML schema.


