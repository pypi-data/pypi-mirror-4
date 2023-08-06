# import gdata.sample_util
import os
import gdata.sites.client
import gdata.sites.data
from export_content import SFWA

try:
    from google_config import *
    config = SITE and USER and PW and EXPORT_FILES
    if not SOURCE:
        SOURCE = '%s-v1' % SITE
except:
    config = False
if not config: 
    print '''Please add a google_config.py file to this directory with the following strings:
             SITE, USER, PW and EXPORT_FILES'''
    print '''These should be the name of the site in Google you are importing to, 
             your Google credentials, and the path to the plone export structure file'''
    exit

# Set site for content creation
client = gdata.sites.client.SitesClient(source=SOURCE, site=SITE)
client.ssl = True  # Force API requests through HTTPS
# Authenticate using your Google Docs email address and password.
client.ClientLogin(USER, PW, client.auth_service)

def export_site(client, structure='', root=''):
    """ Pass in the location of the exported structure folder
        Add the option to import to a location below the root
    """
    if not os.path.exists(structure):
        print 'Sorry the path %s for import was not found' % structure
        return
    elif not os.path.exists(os.path.join(structure,'.objects')):
        print 'Sorry the path %s for import does not contain a .objects file' % structure
        return 

    sfwa = SFWA(client, structure)
    subdir = structure
    if root and root != '/':
        for part in root.split('/'):
            if os.path.exists(os.path.join(subdir, part)):
                subdir = os.path.join(subdir, part)
    sfwa.export(subdir)
    print 'Ran content import for %s' % client.site

def list_sites():
    feed = client.GetSiteFeed()
    for entry in feed.entry:
        if entry.site_name.text == SITE:
            print 'Found requested site: %s (%s)' % (entry.title.text, entry.site_name.text)
            if entry.summary.text:
                print 'description: ' + entry.summary.text
            if entry.FindSourceLink():
                print 'this site was copied from site: ' + entry.FindSourceLink()
            print 'acl feed: %s\n' % entry.FindAclLink()
            print 'theme: ' + entry.theme.text
            return entry
    print 'The site "%s" set in google_config.SITE was not found in your sites, please create it first' % SITE
    return None

site = list_sites()
if not site:
    exit
else:
    export_site(client, structure = EXPORT_FILES)
