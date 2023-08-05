"""Filesystem structure folder importer to Google site
"""
import os, sys
from csv import reader
from csv import writer
from ConfigParser import ConfigParser
from StringIO import StringIO
from types import StringType

#from ilrt.contentmigrator.exportimport.utils import atconvert
#from ilrt.contentmigrator.exportimport.pas import import_users
import gdata.sites.client
import gdata.data
from generic import ShellImportContext

USER_FOLDERS = ['acl_users','Members']

class PrintLog:
    """ Use for simple Log - easier to use in tests
        or for zmi screen output since redirect stdout
        cannot be undone during tests
    """
    def __init__(self, enabled=False):
        self.out = []
        self.enabled = enabled

    def write(self, string):
        if self.enabled:
            self.out.append(string)
        else:
            print string
 
class ClientWrapper():
    """ Wrap the gdata Google API to make it look like the zope context API for 
        modifying content methods
    """
    def __init__(self, client, structure, log=None, replace=True):
        """Hold instance of gdata client to fire these methods at use entry
           as the default 'context' point assuming root if not specified
           if replace then wipe and rebuild existing pages if found
        """
        self.replace = replace
        self.client = client
        self.structure = structure
        self.parent = client.site
        self.feed = self.client.GetContentFeed()
        self.entry = None
        self.log = log

    def setCurrent(self, entry):
        """ Use current as an equivalent to context """
        try:
            self.current = entry.page_name.text
            self.entry = entry
            return self.entry
        except:
            return None

    def contentIds(self):
        """ Content ids is the same as object ids for Google CMS """
        return self.objectIds()

    def objectIds(self, parent=None):
        """ List all objects in a directory """
        if not parent:
            feed = self.feed
        else:
            uri = '%s?parent=%s' % (self.client.MakeContentFeedUri(), self.entry.GetNodeId())
            feed = self.client.GetContentFeed(uri=uri)
        try:
            return [item.page_name.text for item in feed.entry]
        except:
            return []

    def getId(self):
        """ textual id is title whilst entry.GetNodeId() equates to 
            Archetype unique numeric id """
        return self.entry.page_name.text


    def findObject(self, id):
        """ Check object then its children then its parent
            as a form of mini-acquisition 
        """
        if self.current == id:
            return self.entry
        else:
            uri = '%s?parent=%s' % (self.client.MakeContentFeedUri(), self.entry.getNodeId())
            feed = self.client.GetContentFeed(uri=uri)
            for item in feed.entry:
                if item.page_name.text == id:
                    return self.getCurrent(item)
        if self.entry.parent.page_name.text == id:
            return self.entry.parent
        else:
            return None

    def _delObject(self, entry):
        self.log.write('Deleted: %s' % entry.GetAlternateLink().href)
        self.client.Delete(entry)
        return

    def makeObject(self, page_name, kind, subdir, metadict, data, parent=None):
        """ Create content in Google site via feed API """
        title = metadict.get('title', '') or page_name or metadict.get('id','none')
        self.log.write('%s - %s' % (kind, title))
        if not parent:
            parent = self.getObject(subdir = subdir)
        err = None
        if kind == 'attachment':
            path = os.path.join(self.structure, subdir, page_name)
            ms = gdata.data.MediaSource(file_path=path, content_type=metadict.get('content-type',''))
            try:
                entry = self.client.UploadAttachment(ms, parent, 
                                                     title=title, 
                                                     description=metadict.get('description',''))
            except Exception as err:
                self.log.write(err)
            # image_url = 'http://www.google.com/images/logo.gif'
            # web_attachment = self.client.CreateWebAttachment(image_url, 'image/gif', 'GoogleLogo', parent_entry, description='nice colors')
            
        else:
            entry = self.getObject(page_name, subdir)
            if entry:
                if self.replace:
                    self._delObject(entry)
                else:
                    return
            try:
                entry = self.client.CreatePage(kind, title=title, html=data, parent=parent, page_name=page_name)
            except Exception as err:
                self.log.write(err)
        if not err:        
            self.log.write('Created %s. View it at: %s' % (entry.Kind(), 
                                                           entry.GetAlternateLink().href))
            return entry
        return None

    def getObject(self, id = None, subdir = None):
        """ Get object from relative path """
        if subdir:
            path = subdir.replace(self.structure, '')
        else:
            path = ''
        if id:
            path = '%s/%s' % (path, id)
        if path:
            uri = '%s?path=%s' % (self.client.MakeContentFeedUri(), path)
        else:
            return None
        try:
            feed = self.client.GetContentFeed(uri=uri)
        except:
            return None
        if feed and len(feed.entry) == 1:
            return feed.entry[0]
        else:
            return None

class SFWA():
    """ Tree-walking importer for structure folder on the file system

    Folderish instances are mapped to directories within the 'structure'
    portion of the profile, where the folder's relative path within the site
    corresponds to the path of its directory under 'structure'.

    The subobjects of a folderish instance are enumerated in the '.objects'
    file in the corresponding directory.  This file is a CSV file, with one
    row per subobject, with the following wtructure::

     "<subobject id>","<subobject portal_type>"

    Subobjects themselves are represented as individual files or
    subdirectories within the parent's directory.
    If the import step finds that any objects specified to be created by the
    'structure' directory setup already exist, these objects will be deleted
    and then recreated by the profile.  The existence of a '.preserve' file
    within the 'structure' hierarchy allows specification of objects that
    should not be deleted.  '.preserve' files should contain one preserve
    rule per line, with shell-style globbing supported (i.e. 'b*' will match
    all objects w/ id starting w/ 'b'.

    Similarly, a '.delete' file can be used to specify the deletion of any
    objects that exist in the site but are NOT in the 'structure' hierarchy,
    and thus will not be recreated during the import process.

    -----

    ilrt.contentmigrator adapts the importer from the default CMFCore one
    to add binary file, custom archetypes and workflow handling

    """


    def __init__(self, client, structure, log_enabled=False):
        self.structure = structure
        self.log = PrintLog(log_enabled)
        self.client = ClientWrapper(client, structure, self.log)
        self.import_context = ShellImportContext(structure)

    def getLog(self):
        """ Return log """
        if self.log.out:
            return self.log.out
        else:
            return ['Sorry no data written to log, check that it is enabled',]

    def export(self, subdir='', parent=None):
        """ Use googles gdata self.client API see
            http://code.google.com/apis/sites/docs/1.0/developers_guide_python.html
            Recursive function to walk the site
        """

        objects = self.import_context.readDataFile('.objects', subdir)

        if objects is None:
            if subdir:
                self.log.write('There is no .objects in the root folder %s' % subdir)
            return 

        dialect = 'excel'
        stream = StringIO(objects)

        rowiter = reader(stream, dialect)
        ours = filter(None, tuple(rowiter))
        our_ids = set([item[0] for item in ours])

        prior = set(self.client.contentIds())

        preserve = self.import_context.readDataFile('.preserve', subdir)
        if not preserve:
            preserve = set()
        else:
            preservable = prior.intersection(our_ids)
            preserve = set(_globtest(preserve, preservable))

        delete = self.import_context.readDataFile('.delete', subdir)
        if not delete:
            delete= set()
        else:
            deletable = prior.difference(our_ids)
            delete = set(_globtest(delete, deletable))

        # if it's in our_ids and NOT in preserve, or if it's not in
        # our_ids but IS in delete, we're gonna delete it
        delete = our_ids.difference(preserve).union(delete)

        for id in prior.intersection(delete):
            try:
                entry = self.client.getObject(id, subdir)
                if entry:
                    self.client._delObject(entry)
                    self.log.write('Deleted %s' % id)
            except:
                self.log.write('Could not delete %s' % id)
                
        existing = self.client.objectIds()
        # dont create user folders as content, may want Members? 
        existing.extend(USER_FOLDERS)
        path_info = subdir.replace(self.structure,'')
        self.log.write('Adding folder %s with %d objects' % (path_info, len(ours)))

        try:
            for object_id, portal_type in ours:
                if object_id not in existing:
                    obj = self._makeInstance(object_id, portal_type,
                                                subdir, self.import_context, parent)
                    if obj is None:
                        self.log.write("Couldn't make instance: %s%s" %
                                       (path_info, object_id))
                        continue
                    # Equivalent to folderish type if it has a feed of children
                    if obj.feed_link:
                        self.export(os.path.join(subdir, obj.page_name.text), obj)
        except ValueError:
            self.log.write('Aborted import due to format error for %s .objects' % subdir)

    def _makeInstance(self, id, portal_type, subdir, import_context, parent=None):
        """ Add file creation and put_props translation to Google CMS properties 
            which caters for adding workflow and security as exported properites
        """
        path = os.path.join(subdir, id)
        if portal_type.endswith('Criterion') or portal_type in ['Topic',]:
            return None
        if self.import_context.isDirectory(path):
            meta = import_context.readDataFile('.properties', path)
            if os.path.exists(os.path.join(path,'syndication_information')):
                newtype = 'announcementpage'
            else:
                newtype = 'filecabinet'
            data = None
        else:
            data = import_context.readDataFile(id, subdir)
            meta = import_context.readDataFile('%s.ini' % id, subdir)
            if meta and data:
                newtype = 'attachment'
            elif data and type(data) == StringType: 
                parts = data.split("\n\n\n", 1)
                if len(parts) > 1:
                    meta = parts[0]
                    meta = "[DEFAULT]\n%s" % parts[0]
                    data = parts[1]
                else:
                    self.log.write('Found no metadata for obj %s' % id)
                if portal_type in ('News','Event'):
                    newtype = 'announcement'
                else:
                    newtype = 'webpage'
        if newtype:
            metadict = self.get_props(id, meta, import_context, subdir)
            if not data or data == 'None':
                data = ''
            if metadict.get('description', ''):
                data = '<h4>%s</h4>%s' % (metadict['description'], data)
            return self.client.makeObject(page_name=id, kind=newtype, 
                                          subdir=subdir, metadict=metadict, 
                                          data=data, parent=parent)
        else:
            return None
 
    def get_props(self, id, meta, import_context, subdir):
        """
        Update properties from meta
        """
        metadict = {}
        try:
            parser = ConfigParser()
            parser.readfp(StringIO(meta))
            metadict = parser.defaults()
        except:
            self.log.write('Error in metadata format of %s' %
                       os.path.join(subdir, id))

        if metadict:
            return metadict
        else:
            self.log.write('No metadata for %s' % os.path.join(subdir, id))
            return {}
