Google Data API import / export
===============================

Ed Crewe, Feb 2011

Overview
--------

Add utility import and export scripts for migrating plone sites to or from
Google sites. Or migrating folders of content to or from Google docs.

Initial use case was to archive simple old plone sites which had no money for hosting anymore - so even a static dump would be more costly than exporting to
a free Google site, which also still provides a working CMS.

Future use cases may be migrating simple Google sites to Plone when they needed to grow substantially wrt. customisation and features.

Requires the install of gdata from http://code.google.com/p/gdata-python-client/
into 2.2 or later python. Otherwise it is entirely independent of the plone installation since it just requires or creates the structure dump folder.
So the google folder code is command-line only at this time.

Usage
-----

Copy demo_config.py to google_config.py and edit it to point at your google account and site. 

Plone to Google sites export
----------------------------

This first version just handles google site folders and pages. 

NB: Google sites have two other content types, announcements (ie simple news / events) and lists (small data customizable content types).

- Install ilrt.contentmigrator (or ContentMigrator if plone 2) in your plone instance and run the export to a structure directory on the file system.

- Set up a google site and add your google credentials and the site details to
  the google_config.py file along with the path to the exported structure folder then run ...

> python export_to_google.py

Google sites to Plone import
----------------------------

This first version just handles google site folders and pages. 

- For the google site you wish to migrate to plone add the google credentials and the site details to
  the google_config.py file along with the path to where you want the structure folder created as IMPORT_FILES then run ...

> python import_from_google.py

- Install ilrt.contentmigrator in your plone instance and run the import from the structure directory created on the file system by the previous step. 

Google docs to Plone or vice versa
----------------------------------

There is already an application for integrating google docs and plone at
http://pypi.python.org/pypi/collective.googlesharing/1.0.0

However it may be useful to have a one off import / export tool too, but for the moment that may remain on my TODO list until I get a real need to do it.
