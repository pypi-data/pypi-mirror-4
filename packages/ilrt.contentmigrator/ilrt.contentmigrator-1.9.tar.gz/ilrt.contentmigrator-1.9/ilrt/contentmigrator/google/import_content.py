# A basic exporter for the Google Sites API that writes out the site 
# to standard plone export structure on file system - ready for contentmigrator import to plone
# Ed Crewe Feb 2011
from csv import writer
from ConfigParser import ConfigParser
from StringIO import StringIO
import os, shutil
from types import FileType, ListType, TupleType, StringTypes
from config import *
import mimetypes
import re
killtags = re.compile(r'<[^>]*?>')

class GoogleExporter():
    """Uses Google's data API to retrieve the content of a Google site to the
       file system in standard structure folder format ready for Plone import
       Exports content and folder structure
       Content gets default dublin core and metadata in properties files
       Currently custom content types are created as pages with extra properties
       Sorry no user / acl handling or revision handling yet!
    """  

    def __init__(self, client, savepath):
        """ Set savepath and log """
        self.out = []
        if savepath.endswith('structure'):
            parent = savepath[:-len('/structure')]
        else:
            parent = savepath
            savepath = os.path.join(savepath,'structure')
        if os.path.exists(parent):
            self.savepath = savepath
        else:
            raise Exception('Supplied path %s for saving site doesnt exist' % savepath)
        self.client = client
        self.rootlen =  len('https://sites.google.com/site/') 
        self.alternates = []
        self.objlist = {}

    def typemap(self, obj):
        """ Translate types """
        objtype = TYPEMAP.get(obj.Kind(), '')
        if objtype == 'File':
            if obj.content.type.startswith('image'):
                objtype = 'Image'
        return objtype

    def export(self, root='/'):
        """ Based on generic setup folder export to structre -
            See Products.GenericSetup.interfaces.IFilesystemExporter
        """
        feed = self.client.GetSiteFeed()
        site_entry = feed.entry[0]
        site_name = site_entry.site_name.text
        self.out = ['Started export of site %s' % site_name]
        self.rootlen += len(site_name) + 1 

        try:
            if os.path.exists(self.savepath):
                shutil.rmtree(self.savepath)
            os.mkdir(self.savepath)
            self.out.append('Created folder %s' % self.savepath)
        except:
            self.out.append('Failed to create structure folder in %s' % self.savepath)
            return self.out
        # Pull in all folders first since empty ones are missed out of all items 
        uri = '%s?kind=%s' % (self.client.MakeContentFeedUri(), 'filecabinet')
        feed = self.client.GetContentFeed(uri=uri)
        if feed:
            self.write_folder(feed, '/')
        # Now do all items
        feed = self.client.GetContentFeed()
        self.write_folder(feed, '/')        
        # uri = '%s?parent=%s' % (self.client.MakeContentFeedUri(), cfeed.GetNodeId())
        # feed = self.client.GetContentFeed(uri=uri)

        self.write_csv()
        return

    def write_folder(self, feed, path):
        """ Write the contents of feed out to folder
            (the root feed is more like the zcatalog of everything since its not folder based)
        """
        if not feed:
            return

        for obj in getattr(feed, 'entry', []):
            if obj:
                if obj.page_name:
                    id = obj.page_name.text
                    # add fix to move home to front-page
                else:
                    id = obj.title.text
                id = id.encode('ascii','ignore')
                objtype = self.typemap(obj)
                realpath = self.get_web_path(id, obj, path)
                self.obj_record(id, objtype, realpath)
                self.export_object(id,obj,obj.Kind(),realpath)
        

    def get_attr_value(self, obj, attr='summary'):
        """ Attrs can have text or html so check both """
        if hasattr(obj, attr):
            for attr in ('text','html'):
                value = getattr(obj.content, attr, None)
            if value:
                return value
        return ''

    def obj_record(self, id, objtype, path):
        """ Store id, type in dict for path """
        objdict = self.objlist.get(path, {})
        if not objdict.has_key(id):
            objdict[id] = objtype
        self.objlist[path] = objdict
        return

    def write_csv(self):
        """ Close folder CSVs and write them """
        for path, objdict in self.objlist.items():
            ostream = StringIO()
            csv_writer = writer(ostream)
            for id, objtype in objdict.items():
                csv_writer.writerow((id, objtype))
            output = ostream.getvalue()
            # Strip Windows line endings 
            if hasattr(os, 'O_BINARY'):
                output = output.replace('\r','')
            self.write_file(path,'.objects',output)

    def get_web_path(self, id, obj, path=''):
        """ Google stores everything in BigTable against hash getNodeId
            hence the web / fs path is a layer not represented via the atom feed content
            Note: links are returned with spaces removed so must remove them from the id
        """
        try:
            # Gives folder based path whilst GetParentLink is the node id
            link = obj.GetAlternateLink().href
        except:
            try:
                link = obj.GetLink().href
            except:
                link = ''
        if link:
            link = link[self.rootlen:-len(id.replace(' ',''))]
            if not link:
                link = '/'
            return link
            # debug: self.out.append(path)
        if not path:
            path = '/'
        return path

    def export_object(self,id,obj,objtype, path):
        """ export file content to filesystem """
        text = ''
        feed = None
        treatas = 'text'
        if objtype == 'attachment':
            treatas = 'binary'
        else:
            if objtype in ['filecabinet','announcementpage']:
                treatas = 'folder'
            if obj.feed_link:
                feed = self.client.GetContentFeed(uri=obj.feed_link.href)
                if len(feed.entry) > 0:
                    treatas = 'folder'
                else:
                    feed = None
        try:
            html = unicode(obj.content.html)
        except:
            html = ''

        try:
            descrip = self.get_attr_value(obj)
            descrip = killtags.sub('', unicode(descrip))
        except:
            descrip = ''

        if treatas == 'text':
            if html:
                html = html.replace('<html:','<')
                html = html.replace('/html:','/')
                html = '\n\n %s' % html.replace("\r", "")
            if descrip:
                html = 'description: %s\n%s' % (descrip, html)
        else:
            if treatas != 'folder':
                id = self.fix_suffix(id, obj, path)
                if treatas == 'binary':
                    try:
                        self.client.DownloadAttachment(obj, 
                                           self.fsfile(path, id))
                    except:
                        pass

        text = self.properties_marshall(obj, id)
        # do required fields
        for prop, value in PROPS['fixed'].items():
            text += "%s: %s\n" % (prop, value)

        if treatas == 'folder':
            text = self.propini(text, descrip)
            self.write_file(os.path.join(path,id),'.properties',text)
        elif html:
            self.write_file(path,id,text + html)
        else:
            text = self.propini(text, descrip)
            self.write_file(path,id + '.ini',text)

        self.out.append('Wrote %s [%s]' % (obj.title.text, obj.Kind()))
        return 

    def propini(self, text, value):
        """ Start metadata for ini or properties files 
            Currently google API for returning summary html is missing the core data
            so folders description is always empty :-( feb 2011
            even though it uses the start of it for a anchor name, ie.
            just get <html:a name="TOC-start-of-the-summary-text" />
            but leave it in the code in case it starts working
        """
        text = "[DEFAULT]\n%s" % text
        if value and value not in ('False','0'):
            text += 'description: %s\n' % value
        return text

    def fix_suffix(self, id, obj, path):
        """ if file id missing .doc etc. add it here """
        try:
            ctype = obj.content.type
        except:
            return id
        oldid = id
        ext = mimetypes.guess_extension(ctype)
        if id.find('.')==-1:
            id = '%s%s' % (id, ext)
        for key in FIXMIME:
            if id.endswith(key):
                id = id.replace(key,FIXMIME[key])
        if oldid != id:
            self.change_record(oldid, id, path)
        return id

    def change_record(self, oldid, id, path):
        """ Change stored id, type in dict for path """
        objdict = self.objlist.get(path, {})
        if objdict.has_key(oldid):
            objdict[id] = objdict[oldid]
            del(objdict[oldid])
        self.objlist[path] = objdict
        return


    def stringify(self, value):
        """ Ensure properties or fields that are files or other types are
            converted to indented strings and clean up line returns in them """
        if not type(value) in StringTypes:
            value = str(value)
        if value:
            value = value.replace("\r", "")
            if value.endswith("\n"):
                value = value[:-1]
            return value.replace("\n",SEPARATOR)
        return ''

    def properties_marshall(self, obj, id):
        """ Pull out dublin core and
            other basic plone properties
            NB: Google site entries have published state but it doesnt seem to be used yet
        """
        metadata = ''
        for prop in PROPS['id']:
            metadata += '%s: %s\n' % (prop, id)
        if obj.author:
            authors = [author.email.text for author in obj.author]
            names = [author.name.text for author in obj.author]
            metadata += 'owner: %s\n' % authors[0]
            metadata += 'creator: %s\n' % SEPARATOR.join(authors)
            metadata += 'creator_names: %s\n' % SEPARATOR.join(names)
        metadata += 'revision: %s\n' % obj.revision.text
        metadata += 'modification_date: %s\n' % obj.updated.text
        content_type = obj.content.type
        if content_type == 'xhtml':
            content_type = 'text/html' # or 'application/xhtml+xml' ?
        metadata += 'Content-Type: %s\n' % content_type
        try:
            # get first revision date for created
            revisions = self.client.GetRevisionFeed(obj)
            dates = [entry.updated.text for entry in revisions.entry]
            if dates:
                metadata += 'created_date: %s\n' % dates[-1]
            else:
                metadata += 'created_date: %s\n' % obj.updated.text
        except:
            metadata += 'created_date: %s\n' % obj.updated.text
        for prop,md in PROPS['string'].items():
            method, default = md
            data = ''
            if hasattr(obj,method):
                m = getattr(obj,method)
                if m:
                    data = self.stringify(m.text)
            if not data:
                data = default
            metadata += "%s: %s\n" % (prop,data)
        return metadata

    def fsfile(self, path, filename=''):
        """ Get the local file system path for unix or Windows
            from web path
        """
        if not path:
            return filename
        elif path.startswith(self.savepath):
            return path
        folderpath = self.savepath
        for folder in path.split('/'):
            if folder:
                folderpath = os.path.join(folderpath, folder)
            if folderpath:
                if not os.path.exists(folderpath):        
                    try:
                        os.mkdir(folderpath)
                    except:
                        self.out.append('Failed to create or replace ' + folderpath)
                        return
        if filename:
            return os.path.join(folderpath, filename)
        else:
            return folderpath
            
    def write_file(self, path, filename='', data=''):
        """ Save the file directly to the file system var folder
            If no file or data is supplied this just creates a folder
        """
        if filename:
            filepath = self.fsfile(path, filename)
            if os.path.exists(filepath) and os.path.isfile(filepath):
                self.out.append('Deleted %s' % filename)
                os.remove(filepath)
            ofd = None
            try:
                # Treat everything as binary if Windows so line endings dont get tampered with
                if hasattr(os, 'O_BINARY'):
                    ofd = os.open(filepath,os.O_CREAT | os.O_WRONLY | os.O_APPEND | os.O_BINARY)
                else:
                    ofd = os.open(filepath,os.O_CREAT | os.O_WRONLY | os.O_APPEND)
            except:
                self.out.append("Failed to open %s for writing" % filepath)
            if ofd:
                binary = 0
                if type(data) in StringTypes:
                    try:
                        #data = data.replace('html:','')
                        os.write(ofd,data)
                        #self.out.append('Wrote text file %s' % filename)                
                    except UnicodeEncodeError:
                        #data = data.replace('html:','')
                        os.write(ofd, data.encode(DEFAULT_ENCODING))
                        #self.out.append('Wrote unicode file %s' % filename)                
                    except:
                        binary = 1
                else:
                    binary = 1
                if binary:
                    # Try to cope with string buffers or strings or None
                    try:
                        while data is not None:
                            os.write(ofd, data.data)
                            data = data.next
                        self.out.append('Wrote buffered file %s' % filename)                                                
                    except:
                        try:
                            os.write(ofd, data.data)
                            self.out.append('Wrote binary file %s' % filename)                                                
                        except:
                            try:
                                data = str(data.data)
                                if data:
                                    os.write(ofd, data)
                                    self.out.append('Wrote string file %s' % filename)                                                
                            except Exception, error:
                                self.out.append("Sorry failed to write to %s due to %s" % (filepath,error))
                os.close(ofd)
        #debug self.out.append('Wrote %s' % filepath)
        return

        


