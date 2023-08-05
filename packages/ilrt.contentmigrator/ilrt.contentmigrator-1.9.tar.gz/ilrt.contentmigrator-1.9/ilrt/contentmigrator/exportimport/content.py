"""Filesystem exporter / importer adapters.
"""
import os
from csv import reader
from csv import writer
from ConfigParser import ConfigParser
from StringIO import StringIO
from types import StringType

from zope.interface import implements

from Products.GenericSetup.interfaces import IFilesystemExporter
from Products.GenericSetup.interfaces import IFilesystemImporter
from Products.GenericSetup.content import _globtest
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.exportimport.content import StructureFolderWalkingAdapter

from ilrt.contentmigrator.ContentMigrator.config import SEPARATOR
from ilrt.contentmigrator.ContentMigrator.config import PROPS
from ilrt.contentmigrator.exportimport.contentexporter import ContentExporterView
from ilrt.contentmigrator.exportimport.utils import atconvert
from ilrt.contentmigrator.exportimport.pas import import_users

# Requires ilrt.migrationtool to migrate workflow

try:
    from ilrt.migrationtool.browser.workflowtool import WorkflowMigrationView
    MIGRATE_WORKFLOW = True
except:
    MIGRATE_WORKFLOW = False

#
#   setup_tool handlers - required to override content exporter and importer
#

def exportSiteStructure(context, root='/'):
    """ Generic setup export not used because we are reusing the contained standalone
        ContentMigrator Product that can be used for pre generic setup sites """
    portal = context.getSite()
    exporter = ContentExporterView(portal, {})
    exporter.manage_runExport(root, portal)
    #logger = context.get#Logger('SFWA')
    # for line in exporter.getLog():
        #logger.info(line)

def importSiteStructure(context, root='', log=''):
    """ Import users, groups and roles then do content.
        Add the option to import to a location below the root
        then use the subclassed import parts of the SFWA below
    """
    out = []

    userout = import_users(context)
    if userout:
        out.extend(userout)
        
    site = context.getSite()
    if root and root != '/':
        for part in root.split('/'):
            if hasattr(site, part):
                site = getattr(site, part)

    # Dont use IFilesystemImporter(site) since although it runs this SFWA
    # it loses its out log            
    sfwa = SFWA(site)
    sfwa.import_(context, 'structure', True)
    out.append('Run content import to %s' % site.absolute_url())
    sfwaout = getattr(sfwa, 'out')
    if sfwaout:
        out.extend(sfwaout)
    return out

#
#   Filesystem import adapter
#
class SFWA(StructureFolderWalkingAdapter):
    """ Tree-walking exporter for "folderish" types.

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

    implements(IFilesystemExporter, IFilesystemImporter)

    def __init__(self, context):
        self.out = []
        self.context = context
        request = getattr(context,'REQUEST',{})
        self.reindex = request.get('reindex','item')
        if MIGRATE_WORKFLOW:
            self.wfmt = WorkflowMigrationView(context,request)
            self.transmap = {}
        else:
            self.wfmt = None

    def getLog(self):
        """ Log for output to screen
            FIXME: This just uses a list as the log because any reference to
            the generic setup file system logs and getLogger causes thread
            lock and file pickling errors
        """
        return self.out

    def import_(self, import_context, subdir, root=False):
        """ See base SWFA class just replaced refs to Logger with out
        """
        context = self.context

        if not root:
            subdir = '%s/%s' % (subdir, context.getId())

        objects = import_context.readDataFile('.objects', subdir)

        if objects is None:
            if root:
                self.out.append('There is no .objects in the root folder %s' % subdir)
            return 

        dialect = 'excel'
        stream = StringIO(objects)

        rowiter = reader(stream, dialect)
        ours = filter(None, tuple(rowiter))
        our_ids = set([item[0] for item in ours])

        prior = set(context.contentIds())

        preserve = import_context.readDataFile('.preserve', subdir)
        if not preserve:
            preserve = set()
        else:
            preservable = prior.intersection(our_ids)
            preserve = set(_globtest(preserve, preservable))

        delete = import_context.readDataFile('.delete', subdir)
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
                context._delObject(id)
                self.out.append('Deleted %s' % id)
            except:
                self.out.append('Could not delete %s' % id)
                
        existing = context.objectIds()
        self.out.append('Adding folder %s with %d objects' % (context.getId(),len(ours)))

        try:
            for object_id, portal_type in ours:
                if object_id not in existing:
                    #try:
                    object = self._makeInstance(object_id, portal_type,
                                                    subdir, import_context)
                    #except:
                    #    object = None
                    if object is None:
                        self.out.append("Couldn't make instance: %s/%s" %
                                       (subdir, object_id))
                        continue

                wrapped = context._getOb(object_id)
                #Dont use IFilesystemImporter(site) since it wont have the out log
                #Also need to pass log back through recursive class instantiation calls 
                sfwa = SFWA(wrapped)
                sfwa.import_(import_context, subdir)
                self.out.extend(sfwa.out)
            if getattr(self, 'reindex', 'item') == 'all':
                self.refreshCatalog()
        except ValueError:
            err = 'Aborted import due to format error for %s .objects' % subdir
            self.out.append(err)

    def _makeInstance(self, id, portal_type, subdir, import_context):
        """ Add file creation and use local put_props rather than webdav
            which caters for adding workflow and security as exported properites
        """
        context = self.context
        tool = getToolByName(context, 'portal_types')

        try:
            tool.constructContent(portal_type, context, id)
        except ValueError, err: # invalid type
            self.out.append(str(err))
            return None

        obj = context._getOb(id)

        if obj.isPrincipiaFolderish:
            meta = import_context.readDataFile('.properties',
                                                 '%s/%s' % (subdir, id))
            if meta:
                self.put_props(obj, meta, import_context, subdir)
        else:
            data = import_context.readDataFile(id, subdir)
            meta = import_context.readDataFile('%s.ini' % id, subdir)
            if meta:
                self.put_props(obj, meta, import_context, subdir)
                content_type = obj.getProperty('format', obj.getProperty('ContentType',''))
                if data:
                    if portal_type == 'Image' or content_type.startswith('image'):
                        obj.setImage(data) #plone 4 doesnt take content_type arg
                    else:
                        obj.setFile(data)
            else:
                # Standard page objects get metadata anyway via dummy webdav handling
                # This ensures that file fields and workflow are also handled
                if data and type(data) == StringType: 
                    parts = data.split("\n\n\n", 1)
                    if len(parts) > 1:
                        meta = parts[0]
                        meta = "[DEFAULT]\n%s" % parts[0]
                        if hasattr(obj, 'setText'):
                            obj.setText(parts[1], mimetype='text/html')
                        else:
                            try:
                                obj['text'] = parts[1]
                            except:
                                pass
                    else:
                        self.out.append('Found no metadata for obj %s' % obj.getId())
                    self.put_props(obj, meta, import_context, subdir)

        if getattr(self, 'reindex', 'item') == 'item':
            obj.indexObject()

        return obj

    def put_props(self, obj, meta, import_context, subdir):
        """
        Update properties from meta
        """
        metadict = {}
        try:
            parser = ConfigParser()
            parser.readfp(StringIO(meta))
            metadict = parser.defaults()
        except:
            self.out.append('Error in metadata format of %s' %
                       os.path.join(subdir, obj.getId()))

        if metadict:
            self.at_demarshall(obj, metadict, import_context, subdir)
            self.properties_demarshall(obj, metadict)
            if MIGRATE_WORKFLOW:
                self.workflow(obj, metadict, import_context)
        else:
            self.out.append('No metadata for %s' % os.path.join(subdir, obj.getId()))
            
    def do_transitions(self, obj, wf, from_state, to_state):
        """ Perform transistions to move from_state to to_state
            Get ilrt.migrationtool workflow transistion maps and cache locally
        """
        tm = self.transmap.get(wf,{})
        if not tm:
            tm = self.wfmt.getTransitionStateMap(wf)
            self.transmap[wf] = tm
        transpath = tm.get('%s>%s' % (from_state,to_state),[])
        workflow = self.wfmt.workflow_tool.getWorkflowById(wf)
        for trans in transpath:
            self.wfmt._tryTransition(workflow=workflow,
                                     obj=obj,
                                     transition=trans,
                                     comment='Content migrator import')
            if self.wfmt.workflow_tool.getInfoFor(obj, 'review_state',
                                                  wf) == from_state:
                self.out.append("Object %s cannot be migrated to state %s" % \
                              ('/'.join(obj.getPhysicalPath()), to_state))
        return

    def workflow(self, obj, metadict, import_context):
        """ Get list of workflows and matching states as lines fields
            If no workflows are in common then set state of default workflow
            to the first one listed for the object's exported metadata
            - if the default workflow has a matching state, else log it 

            This function requires ilrt.migrationtool
        """
        chain = self.wfmt.workflow_tool.getChainFor(obj)
        flag_done = 0
        if chain:
            states = metadict.get('states','').split('SEPARATOR')
            if states:
                workflows = metadict.get('workflows','').split('SEPARATOR')
                if len(workflows) == len(states):
                    for i, wf in enumerate(workflows):
                        if wf in chain: 
                            from_state = self.wfmt.workflow_tool.getInfoFor(obj,
                                                           'review_state',wf)
                            if states[i] != from_state:
                                self.do_transitions(obj, wf,
                                                    from_state, states[i])
                                flag_done = 1
                if not flag_done:
                    wf = chain[0]
                    from_state = self.wfmt.workflow_tool.getInfoFor(obj,
                                                    'review_state',wf)
                    if states[0] != from_state:
                        self.do_transitions(obj, wf, from_state, states[0])
                        return 
        return

    def at_demarshall(self, obj, metadata, import_context, subdir):
        """ Check whether object is an archetype and if so
            marshall the fields to properties text
            Uses a dictionary of at field type converter methods
            Case insensitive check of metadata keys
        """
        if not hasattr(obj,'Schema'):
            return ''
        text = ''
        p = obj.getPrimaryField()
        pname = p and p.getName() or None

        #debug fieldnames = [f.getName() for f in obj.Schema().fields()]
        #debug self.out.append('at_demarshall metadata %s' % str(metadata.keys()))
        #debug self.out.append('at_demarshall to fields %s' % str(fieldnames))        

        fields = obj.Schema().fields()

        if pname in fields:
            fields.remove(pname)
        for f in fields:
            name = f.getName()
            # Stop setting text without html mimetype
            if name == 'text':
                continue
            value = metadata.get(name, metadata.get(name.lower(), None))
            #debug self.out.append('add %s - %s = %s' % (typename, name, value))
            if value:
                typename = f.type 
                written = False
                if typename in ('file', 'image'):
                    if value == 'EXTRAFILE':
                        filename = '%s.%s' % (obj.getId(), name)
                        data = import_context.readDataFile(filename, subdir)
                        mutator = f.getMutator(obj)
                        if mutator:
                            mutator(data)
                            written = True
                    if value == 'DATAFILE':
                        written = True
                else:
                    if typename in atconvert.keys():
                        value = atconvert[typename](value)
                    mutator = f.getMutator(obj)
                    if mutator:
                        try:
                            mutator(value)
                            written = True
                        except:
                            written = False
                        #debug self.out.append(
                        #   'convert %s to %s and add with %s' % (invalue, value, mutator))
                if not written:
                    self.out.append('Failed to update %s %s.%s = %s' % (subdir,
                                                     obj.getId(), name, value))
                    
    def properties_demarshall(self, obj, metadata):
        """ Pull out dublin core properties
        """
        for key, value in metadata.items():
            if key == 'text':
                continue
            if value:
                if type(value)!=StringType and type(value) in [ListType, TupleType]:
                    value = value.split(SEPARATOR)
                if obj.hasProperty(key) and value:
                    try:
                        obj._updateProperty(key, value)
                    except:
                        setattr(obj, key, value)
        return

    def refreshCatalog(self):
        """ Taken from ZCatalog but with metadata preserved -
            re-index everything we can find
            TODO: see if this really makes a difference from
            catalog.refreshCatalog()
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        cat = catalog._catalog
        paths = cat.paths.values()
        paths = tuple(paths)
        cat.clear()
        num_objects = len(paths)
        for i in xrange(num_objects):
            p = paths[i]
            obj = catalog.resolve_path(p)
            if obj is None:
                obj = catalog.resolve_url(p, catalog.REQUEST)
            if obj is not None:
                try:
                    catalog.catalog_object(obj, p, update_metadata=0)
                except ConflictError:
                    pass

