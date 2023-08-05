ILRT Content Migrator
=====================

Ed Crewe, `ILRT
<http://www.ilrt.bris.ac.uk/>`_ at University of Bristol, Oct 2012

Updated from plone 3.* version 0.6 to plone 4.* compatible version 1.6
There are no functional changes between 0.6 and 1.6, in terms of the
plone export / import just extra version compatibility tweaks and update of
the test suite. 

However there is also the addition of tool to migrate plone exported sites to
Google sites or vice versa, see http://sites.google.com
Either moving legacy plone sites to free hosting, or increasing the 
customisation level of a site, beyond Google sites remit. Either way I hope this 
tool may prove mutally beneficial. 

See http://bitbucket.org/edcrewe/ilrt.contentmigrator for mercurial source 
repository, issue tracker etc.

NOTE: Export should work (to some extent) for all plone versions.

Overview
--------

This egg and the companion Product it contains was written to migrate content 
from pre-Archetypes plone 2.0 sites (or later) to current plone.

The ilrt.contentmigrator egg extends the generic setup content import system 
to handle binary files and custom content. Hence a fully populated
site can be generated from file system content held in a profiles structure 
folder.

The egg follows the paradigm of the existing generic setup, but adds workflow 
state to the properties metadata. 
It also adds *.*.ini files for each binary content item so that these can 
have all their associated metadata imported and exported.

It contains a companion old-style plone product. This can be dropped into the 
Products folder in an old plone site.
The site gains a portal_exportcontent tool. Running the export from this
tool exports the content to a structure folder in the var directory ready 
for using to populate a current plone site, and hence migrate the content.

Concept
-------

The code was arrived at due to the need to migrate a large number of obselete
plone sites and having researched the issue, found that most tools assumed a plone 
version within the last few years, where Archetypes, Five, Marshall and XML, or in 
place content migration is viable.

Instead the code applies the methodology discussed in Andreas Jungs' blog posting 
`Plone migration fails - doing content-migration only
<http://www.zopyx.com/blog/when-the-plone-migration-fails-doing-content-migration-only>`_

Using the Content Migrator
--------------------------

Copy ilrt.contentmigrator/Products/ContentMigrator to the Products directory of 
the old plone site. Restart and you should have a 'Content Migrator Tool' listed
in the right hand content drop down. Pick this and add it to the portal.

There will be a new portal_exportcontent tool in your site. Select this and choose
the Export content tab.
Click export and wait whilst you site becomes files in var/zope/structure
If you only wish to export a subsection of your site then specify the path in the 
textbox at the top of the page.

Go to your new plone install. Add ilrt.contentmigrator to your buildout config 
eggs and zcml sections then run bin/buildout. 

To do a full import you must first install ilrt.contentmigrator via the quick installer.

Add a plone site if you are not importing to an existing one. Go to the ZMI
via http://host/Plone/manage and click on the portal_quickinstaller tool 
Select Content Migrator Tool Install  check the box and click Install.
You should then have /Plone/portal_setupcontent available. Click on that
to access the migrator interface.

Copy (or symlink) the exported structure folder to a profile folder either in the 
ilrt.contentmigrator egg or in the main theme egg for your new plone site 
and restart, eg. ilrt.contentmigrator/ilrt/contentmigrator/profiles/import/structure 

Further details
---------------

When the contentmigrator tool is installed, the content adapter for generic setup will 
be modified so that the content import step will now add all content and set workflow states.

Hence generic setup, ie Plone/portal_setup is required as the base for this tool.

When you go to the new portal_setupcontent tool you can run a further enhanced 
version of the generic setup content step that also sets up users, groups and 
memberdata and provides fuller logging to screen.
In addition the tool provides access to the exporter so that you can re-export a site 
or a subfolder of its content.

If you wish to specify another path for the structure folder import just adjust
the directory in the profile that you are using e.g. directory="c:\\import" 
in profiles.zcml 

If a default profile is used then generic setup will automatically create
the content when the egg with the profile is reinstalled or selected for Plone site
creation. Where as if another profile is used (such as /import above) then it has to 
be manually selected first and then run via the setup tool or this migrator tool. 
For large content imports this is likely to be preferable.

Standard generic setup runs the adapter in CMFCore.exportimport.content which will 
only populate content for HTML documents, and no properties or workflow states will 
be added. 

The ilrt.contentmigrator modifies the generic setup site creation to do the following

  - Populate binary content formats and archetypes if matching ones are found. 
  - Use Marshall's RFC822 marshaller to extract and apply the properties data.
  - Apply workflow state transitions.
    NB: The workflow migration requires the 
    `ilrt.migrationtool 
    <http://pypi.python.org/pypi/ilrt.migrationtool>`_ egg.
  - Translate old content types and add memberdata (see below)

Please note that the import takes much longer than the export.
So for example a Gigabyte of content might only take 5 minutes to export, but take
an hour to import! 

Content Types Translation
-------------------------

There is a mapping of old types to newer archetypes for old plone sites.
Currently this just handles 'Calendar Item' to 'Event' and 'Link' to 'ATLink'.
It is in the ilrt/contentmigrator/ContentMigrator/config.py file.
By modifying the TYPEMAP and NONATPROPS dictionaries of configuration data you can map 
other old custom types to new content, or even use it to migrate content from one new type 
to another.

User migration
--------------

The contentmigrator will also export and import zope held users, including passwords.
It does so by generating the user, roles and groups data from GRUF or 
PAS based sites as generic setup xml files in the /structure/acl_users folder.
Memberdata is saved as a csv file for each member in the portal_memberdata directory 
within acl_users.

Google sites import
-------------------

The Google sites import is outside of plone. 
It just requires command line python with Googles gdata library installed. 
Please see the ilrt.contentmigrator/ilrt/contentmigrator/google/README.txt
NB: Currently it doesnt handle custom content types

XML Format
----------

There is an option to export content as XML for importing into other systems, 
for reimporting into current Plone, stick with the default CSV format.
