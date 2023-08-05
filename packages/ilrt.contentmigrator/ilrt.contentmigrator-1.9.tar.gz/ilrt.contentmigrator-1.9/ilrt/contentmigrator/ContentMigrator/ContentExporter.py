# Make a structure exporter that works with plone 2.0
from csv import writer, QUOTE_MINIMAL
from xml.dom.minidom import getDOMImplementation
from ConfigParser import ConfigParser
from StringIO import StringIO
import os, shutil
from types import FileType, ListType, TupleType, StringTypes
from Globals import InitializeClass

from AccessControl import ClassSecurityInfo, AuthEncoding
from AccessControl.Permissions import use_mailhost_services
from Acquisition import aq_inner
from OFS.SimpleItem import SimpleItem
from OFS.Image import File
from DateTime import DateTime
import time

try:
    from Products.CMFCore.permissions import ManagePortal
except ImportError:
    from Products.CMFCore.CMFCorePermissions import ManagePortal

try:
    set()
except NameError:
    from sets import Set as set

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName

import zLOG
from config import SEPARATOR, PROPS, ALLPROPS, NONATPROPS, TYPEMAP, DEFAULT_ENCODING
try:
    from App.special_dtml import DTMLFile
except:
    from Globals import DTMLFile

class ContentExporter(UniqueObject, SimpleItem):
    """An old school Product for plone 2 that sucks out content into plone 3
       generic setup style structure. From Andreas Jung's idea
       http://www.zopyx.com/blog/when-the-plone-migration-fails-doing-content-migration-only
       Exports content and folder structure
       Content gets default dublin core and workflow metadata in properties files
       If archetypes are found their schema data is added to the properties.
    """  

    try:
        __implements__ = (SimpleItem.__implements__,)
    except:
        pass
        
    meta_type = 'Content Exporter Tool'
    plone_tool = 1
    id = 'portal_exportcontent'
    title = 'Exports content from pre-plone 3 site to generic setup structure folder'
    security = ClassSecurityInfo()

    manage_options = ( ({ 'label' : 'Overview', 'action' : 'manage_overview' }
                     ,  { 'label' : 'Export content', 'action' : 'manage_export' }
                     ,
                     )
                     )

    #
    #   ZMI methods
    #
    security.declareProtected( ManagePortal, 'manage_overview' )
    manage_overview = PageTemplateFile(os.path.join('www','explainContentMigrator.pt'), globals(),
                                   __name__='manage_overview')

    security.declareProtected( ManagePortal, 'manage_export' )
    manage_export = PageTemplateFile(os.path.join('www','exportContentMigrator.pt'), globals(),
                                   __name__='manage_export')

    def __init__(self):
        """ Set savepath and log """
        self.savepath = self.get_var_path()
        self.out = []
        self.format = 'CSV'
        self.dom = None

    def write_folder_element(self, id, objtype, doc):
        """ XML folders best gathered by type and listed """
        if self.format == 'XML':
            text = doc[0].createTextNode(id)
            name = objtype.lower()
            name = name.replace(' ','')
            child = doc[0].createElement(name)
            child.appendChild(text)
            plural = '%ss' % name
            nodes = doc[0].getElementsByTagName(plural)
            if nodes:
                element = nodes[0]
            else:
                element = doc[0].createElement(plural)
            element.appendChild(child)
            doc[1].appendChild(element)            
        else:
            self.write_element(name=id, data=objtype, doc=doc, space=False)

    def write_element(self, name, data, listed=False, doc=None, space=True):
        """ abstract output writing to allow different formats """
        if self.format == 'XML':
            node = None
            if listed:
                if name.endswith('s'):
                    item_name = name[:-1]
                else:
                    item_name = 'item'
                node = doc[0].createElement(item_name)
                for item in data:
                    text = doc[0].createTextNode(item)
                    node.appendChild(text)
            else:
                try:
                    node = doc[0].createTextNode(data)
                except:
                    pass
            if node:
                element = doc[0].createElement(name)
                element.appendChild(node)
                doc[1].appendChild(element)
        else:
            if listed:
                if data:
                    data = SEPARATOR.join(data)
                else:
                    data = ''
            if space:
                doc[1].writerow((name, ' %s' % data))
            else:
                doc[1].writerow((name, data))
            return 

    def get_doc(self, delimiter=':'):
        """ Get doc as xml minidom or csv string stream
            and its writer as a tuple  
        """
        if self.format == 'XML':
            if delimiter == ',':
                tag = 'items'
            else:
                tag = 'properties'
            doc = self.dom.createDocument(None, tag, None)
            node = doc.documentElement
            return (doc, node)
        else:
            ostream = StringIO()
            return (ostream, writer(ostream,
                                    delimiter=delimiter,
                                    quoting=QUOTE_MINIMAL))

    def get_output(self, doc, headfoot=None):
        """ get output from doc for writing to file
            Unfortunately csv or xml writers both 
            require some minor format and header of footer tweaks
        """
        if self.format == 'XML':
            output = doc[0].toprettyxml(indent="  ")
            if headfoot and headfoot != 'DEFAULT':
                # Add html at end of xml
                return output.replace('</properties>',
                                      '''<html><![CDATA[\n%s]]></html>
                                         \n</properties>''' % headfoot)
            else:
                return output
        else:
            if headfoot == 'DEFAULT':
                output = "[%s]\n%s" % (headfoot, doc[0].getvalue())
            elif headfoot:
                output = "%s\n\n%s" % (doc[0].getvalue(), headfoot)                
            else:
                output = doc[0].getvalue()
            #if hasattr(os, 'O_BINARY'):
            #    output = output.replace('"\r','')
            #    output = output.replace("\r", '')
            # kill minimal quotes
            output = output.replace('\r', '')
            output = output.replace('"\n', '\n')
            output = output.replace(':" ', ': ')
            return output
        return 'NO FORMAT SUPPLIED'
        
    def get_var_path(self):
        """ Find var if buildout or old style zope layout or
            test runner where instance home is the buildout-cache!
        """
        var = os.path.join(INSTANCE_HOME, 'var')
        if os.path.exists(var):
            return os.path.join(var, 'structure')
        for folder in ['parts', 'buildout-cache']:
            parts = INSTANCE_HOME.find(folder)
            if parts>-1:
                if os.path.exists(os.path.join(INSTANCE_HOME[0:parts], 'var')):
                    return os.path.join(var,'structure')
                else:
                    return os.path.join(INSTANCE_HOME[0:parts], 'structure')
        for var in ['/tmp', '\\temp']:
            if os.path.exists(var):
                return os.path.join(var, 'structure')


    security.declareProtected( ManagePortal, 'manage_runExport' )
    def manage_runExport(self, portal=None, root=''):
        """ run the export if root submitted -
            option to pass in the portal object so this can be run
            more easily by external scripts
        """
        request = getattr(self, 'REQUEST', {})
        if not root:
            root = request.get('root', '')
        format = request.get('format', 'CSV')
        if root:
            if not portal:
                portal = getToolByName(self, 'portal_url').getPortalObject()
            self.export(root=root,
                        portal=portal,
                        users=request.get('exportusers', None),
                        format = format
                        )
        #if self.dom:
        #    self.dom.unlink()
        if hasattr(request, 'RESPONSE'):
            request.RESPONSE.redirect('manage_export')

    security.declareProtected( ManagePortal, 'getLog' )
    def getLog(self):
        """ return the out log file of export actions """
        return self.out 
    
    def write_file(self, path, filename='', data='', modified=None):
        """ Save the file directly to the file system var folder
            If no file or data is supplied this just creates a folder
        """
        currentpath = self.savepath
        for folder in path.split('/'):
            if folder:
                folderpath = os.path.join(currentpath, folder)
            else:
                folderpath = self.savepath
            if folderpath:
                if not os.path.exists(folderpath):        
                    try:
                        os.mkdir(folderpath)
                        self.out.append('Created %s' % folderpath)
                    except:
                        self.out.append('Failed to create or replace ' + folderpath)
                        return
                currentpath = folderpath

        if filename:
            if self.format == 'XML':
                if filename.startswith('.'):
                    filename = '%s.xml' % filename
                elif filename.endswith('.html'):
                    filename = filename.replace('.html', '.xml')
            filepath=os.path.join(folderpath, filename)
            if os.path.exists(filepath) and os.path.isfile(filepath):
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
                        os.write(ofd,data)
                    except UnicodeEncodeError:
                        os.write(ofd, data.encode(DEFAULT_ENCODING))
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
                    except:
                        try:
                            os.write(ofd, data.data)
                        except:
                            try:
                                data = str(data.data)
                                if data:
                                    os.write(ofd, data)
                            except Exception, error:
                                self.out.append("Sorry failed to write to %s due to %s" % (filepath,error))
                self.set_times(ofd, modified)
                os.close(ofd)
        #debug self.out.append('Wrote %s' % filepath)
        return

    def set_times(self, ofd, modified):
        """ Set the last access and modified time for the file system """
        if modified:
            try:
                times = (time.time(), modified.timeTime())
                os.utime(ofd, times)
            except:
                pass
        return

    def export_users(self, portal):
        """ Write out users and roles in generic setup XML format
            Dump memberdata contents in RFC822 csv format
        """
        folderdoc = self.get_doc(delimiter=',')        
        membership = getToolByName(portal, 'portal_membership')
        memberdata = getToolByName(portal, 'portal_memberdata')
        self.write_file('/acl_users','','')
        path = '/acl_users/portal_memberdata'
        user_info = []
        for user_id in memberdata._members.keys():
            u = membership.getMemberById(user_id)
            if u is not None:
                self.write_element(name=user_id, data='Memberdata',
                                   doc=folderdoc, space=False)                
                doc = self.get_doc()
                try:
                    password = portal.acl_users._user_passwords[user_id]
                except:
                    password = u.getPassword()
                    if password and not AuthEncoding.is_encrypted(password):
                        password = AuthEncoding.pw_encrypt(password)
                if not password:
                    password = 'this user is going to need a password reset'
                    
                info = {'user_id': user_id,
                        'login_name': u.getProperty('login_name',user_id),
                        'password_hash': password,
                       }
                user_info.append(info)
                for prop in memberdata.propertyIds():
                    data = u.getProperty(prop)
                    if data:
                        self.write_element(name=prop, data=data, doc=doc)
                user_output = self.get_output(doc)
                if self.format == 'XML':
                    self.write_file(path, '%s.xml' % user_id, user_output)
                else:
                    self.write_file(path, user_id, "[DEFAULT]\n%s" % user_output)
                #TODO: add portait export
                #obj = memberdata._getPortrait(user_id)
                #if obj:
                #    self.write_file(path,'%s.jpg' % user_id,obj.data)

        info = {}
        info['title'] = 'source_users'
        info['users'] = user_info
        template = DTMLFile(os.path.join('xml', 'zodbusers.xml'),
                            globals()).__of__(portal) 
        self.write_file('/acl_users', 'source_users.xml', template(options=info))
        template = DTMLFile(os.path.join('xml', 'zodbroles.xml'),
                            globals()).__of__(portal) 
        info = self._getRoleInfo(portal)
        self.write_file('/acl_users', 'portal_role_manager.xml',
                                            template(options=info))
        template = DTMLFile(os.path.join('xml', 'zodbgroups.xml'),
                            globals()).__of__(portal) 
        info = self._getGroupInfo(portal)
        self.write_file('/acl_users', 'source_groups.xml',
                                     template(options=info))
        output = self.get_output(folderdoc)
        # strip Windows line endings
        if hasattr(os, 'O_BINARY'):
            output = output.replace('\r', '')
        self.write_file(path, '.objects', output)
        self.out.append('Exported member data')

    def _getRoleInfo(self, portal):
        """ Does the same as method in PluggableAuthService exportimport
            but doesnt require PAS
        """
        role_info = []
        try:
            allroles = portal.acl_users.listRoleInfo()
        except:
            try:
                allroles = portal.portal_membership.getCandidateLocalRoles(portal)
            except:
                allroles = portal.__ac_roles__
        try:
            userroles = portal.acl_users._principal_roles.items()
        except:
            userroles = portal.acl_users.getLocalRolesForDisplay(portal)            
        for role_id in allroles:
            info = {'role_id': role_id,
                    'title': role_id,
                    'description': '',
                   }
            info['principals'] = self._listRolePrincipals(userroles,
                                                          role_id) 
            role_info.append(info)

        return {'title': 'portal_role_manager',
                'roles': role_info,
               }

    def _listRolePrincipals(self, userroles, role_id):
        """ Does the same as method in PluggableAuthService exportimport
            but doesnt require PAS
        """
        result = []
        for userrole in userroles:
            if role_id in userrole[1]:
                result.append(userrole[0])
        return tuple(result)


    def _getGroupInfo(self, portal):
        """ Does the same as method in PluggableAuthService exportimport
            but doesnt require PAS
        """
        group_info = []
        try:
            allgroups = portal.acl_users.listGroupInfo()
        except:
            allgroups = portal.portal_groups.listGroupIds()
        try:
            usergroups = portal.acl_users._principal_groups.items()
        except:
            usergroups = None
        for group_id in allgroups:
            info = {'group_id': group_id,
                    'title': group_id,
                    'description': '',
                   }
            if usergroups:
                info['principals'] = self._listRolePrincipals(usergroups,
                                                              group_id) 
            else:
                group = portal.portal_groups.getGroupById(group_id)
                try:
                    info['principals'] = group.getGroupMembers(group_id)
                except:
                    info['principals'] = group.getGroupMembers()
                
            group_info.append(info)

        return {'title': 'local_roles',
                'groups': group_info,
               }

    def write_folder(self, folder, path):
        """ Write the contents of folder out """
        folderdoc = self.get_doc(delimiter=',')
        path = path[self.lenportal:]

        for id in folder.objectIds():
            if not id.startswith('.'):
                obj = getattr(folder,id,None)
                # getTypeInfo can return Folder for python scripts so check
                if obj and not str(obj) == '<PythonScript at %s>' % id:
                    try:
                        objtype = obj.getTypeInfo().getId()
                        objtype = TYPEMAP.get(objtype, objtype)
                    except:
                        objtype = None
                    if objtype:
                        doc = self.get_doc()
                        self.export_object(id, obj, objtype, path, doc)
                        self.write_folder_element(id=id, objtype=objtype,
                                                  doc=folderdoc)
        output = self.get_output(folderdoc)
        # Strip Windows line endings 
        if hasattr(os, 'O_BINARY'):
            output = output.replace('\r', '')
        self.write_file(path, '.objects', output)

    def export(self, portal, root='/', users='yes', format='CSV', request={}):
        """ Based on generic setup folder export to structre -
            See Products.GenericSetup.interfaces.IFilesystemExporter
        """
        self.format = format
        if format == 'XML':
            self.dom = getDOMImplementation()
        self.workflow_tool = getToolByName(portal, 'portal_workflow')
        portalname = portal.getId()
        self.lenportal = len(portalname) + 1
        self.out = ['Log started at %s' % DateTime()]
        # Give this a request attribute since some methods expect it
        # and it is not available when used via current plone 
        if not hasattr(self, 'REQUEST'):
            self.REQUEST = request

        try:
            if os.path.exists(self.savepath):
                shutil.rmtree(self.savepath)
            os.mkdir(self.savepath)
        except:
            self.out.append('Failed to create structure folder in %s' % self.savepath)
            return self.out

        if users:
            try:
                self.export_users(portal)
            except:
                self.out.append('Sorry not all users could be exported.')

        if not root.startswith('/'):
            root = '/%s' % root
        if len(root) > 1 and not root.startswith('/%s/' % portalname):            
            root = '/%s%s' % (portalname, root)            
        catalog = getToolByName(portal, 'portal_catalog')
        # Just return everything then filter for folderish later
        results = catalog(path={'query': root})
        # exportable = portal.contentItems()
        self.out.append('Exporting %s content items to zope/var/structure' % len(results))
        
        if root == '/':    
            self.write_folder(portal, '/')
        elif results:
            rootpath = root.split('/')
            if len(rootpath)>1:
                rootobj = getattr(portal, rootpath[2], None)
                if rootobj:
                    id = rootobj.getId()
                    objtype = rootobj.getTypeInfo().getId()
                    folderdoc = self.get_doc(delimiter=',')
                    self.write_folder_element(id=id, objtype=objtype,
                                              doc=folderdoc)
                    self.write_file('/',
                                    '.objects',
                                    self.get_output(folderdoc)
                                    )
                    doc = self.get_doc()                    
                    self.export_object(id, rootobj, objtype, '/', doc)
        for brain in results:
            try:
                obj = brain.getObject(self.REQUEST)
            except:
                obj = None
                self.out.append('Object %s at %s was not traversable' % (brain.getId,
                                                                         brain.getPath()))
            if obj and obj.isPrincipiaFolderish:
                path = brain.getPath()
                self.write_folder(obj, path)

        return self.out


    def export_object(self, id, obj, objtype, path, doc):
        """ export file content to filesystem """
        modified = self.properties_marshall(obj, doc)
        # do required fields
        for prop, data in PROPS['fixed'].items():
            propname = prop
            prop = PROPS['boolean'].get(prop, prop)
            if hasattr(obj, prop):
                if getattr(obj, prop, None):
                    data = True
                else:
                    data = False
            self.write_element(name=propname,
                               data=data,
                               doc=doc)
        self.workflow(obj, doc)
        self.at_marshall(obj, path, doc)

        if hasattr(obj,'data'):
            treatas = 'binary'
        elif obj.isPrincipiaFolderish:
            treatas = 'folder'
        else:
            treatas = 'text'

        if treatas == 'text':
            try:
                value = obj['text']
            except:
                value = getattr(obj, 'text', '')
            if value:
                if type(value) not in StringTypes:
                    value = str(value)
                output = self.get_output(doc, value.replace('\r', ""))
                self.write_file(path, id, output, modified)
        else:
            if treatas == 'folder':
                self.write_file(os.path.join(path, id), '.properties',
                                self.get_output(doc, 'DEFAULT'))
            else:
                self.write_file(path, id + '.ini', self.get_output(doc, 'DEFAULT'))
                self.write_file(path, id, obj.data, modified)
        return

    def workflow(self, obj, doc):
        """ Get list of workflows and matching states as lines fields """
        chain = self.workflow_tool.getChainFor(obj)
        if chain:
            self.write_element(name='workflows', data=chain,
                               listed=True, doc=doc)
            states = []
            for wf_id in chain: 
                states.append(self.workflow_tool.getInfoFor(obj, 'review_state', wf_id))
            self.write_element(name='states', data=states,
                               listed=True, doc=doc)            
        return 

    def stringify(self, value):
        """ Ensure properties or fields that are files or other types are
            converted to indented strings and clean up line returns in them """
        if isinstance(value, File):
            value = getattr(value, 'data', value)
        if not type(value) in StringTypes:
            value = str(value)
        value = value.replace("\r", "")
        if value.endswith("\n"):
            value = value[:-1]
        return value.replace("\n",SEPARATOR)

    def at_marshall(self, obj, path, doc):
        """ Check whether object is an archetype and if so
            marshall the fields to properties text and save file field objects"""
        if not hasattr(obj,'Schema'):
            return ''
        p = obj.getPrimaryField()
        pname = p and p.getName() or None
        fields = obj.Schema().fields()
        #[f for f in obj.Schema().fields()
        #          if f.getName() not in ALLPROPS]
        if pname in fields:
            fields.remove(pname)
        for f in fields:
            name = f.getName()
            try:
                value = obj[name]
            except:
                value = None
            #FIXME: check to see if this file is the data file rather than only
            # doing extra files for objects with no data attribute.
            if f.type in ('file', 'image'):
                if not hasattr(obj, 'data'):
                    filename = '%s.%s' % (obj.getId(), name)
                    self.write_file(path, filename, value)                
                    value = 'EXTRAFILE'
                else:
                    value = 'DATAFILE'
            #TODO: Add GSXML style ATReference handling all archetypes in plone 2.1 or later        
            if value != None:
                listed = False
                if type(value) not in StringTypes and type(value) in [ListType, TupleType]:
                    if value:
                        data = [self.stringify(v) for v in value]
                        listed = True
                else:
                    data = self.stringify(value)
                self.write_element(name=name, data=data,
                                   listed=listed, doc=doc)
        return 

    def properties_marshall(self, obj, doc):
        """ Pull out dublin core, workflow state and
            other basic plone properties 
        """
        modified = None
        for prop, method in PROPS['string'].items():
            if hasattr(obj,method):
                data = self.stringify(getattr(obj, method)())
            else:
                data = ''
            self.write_element(name=prop, data=data, doc=doc)
        for prop, method in PROPS['date'].items():
            if hasattr(obj, method):
                data = str(getattr(obj, method)())
            if not data:
                data = 'None'
            else:
                if prop == 'modification_date':
                    modified = data
            self.write_element(name=prop, data=data, doc=doc)        
        for prop, method in PROPS['list'].items():
            me = getattr(obj, method, None)
            if me:
                data = [self.stringify(v) for v in me()]
                listed = True 
            else:
                data = ''
                listed = False
            self.write_element(name=prop, data=data,
                                          listed=listed, doc=doc)
        creators = []
        for prop,method in PROPS['user'].items():
            if hasattr(obj,method):
                data = str(getattr(obj,method)())
                creators.append(data)
            else:
                data = ''
            self.write_element(name=prop, data=data, doc=doc)
        if creators:
            creators = set(creators)
            self.write_element(name='creators', data=creators,
                               listed=True, doc=doc)
        objtype = obj.getTypeInfo().getId()
        if objtype in TYPEMAP.keys():
            propmap = NONATPROPS[objtype]
            for prop in propmap.keys():
                if hasattr(obj,prop):
                    data = self.stringify(getattr(obj, prop, ''))
                    self.write_element(name=propmap[prop],
                                       data=data, doc=doc)
        return modified
        
InitializeClass(ContentExporter)

