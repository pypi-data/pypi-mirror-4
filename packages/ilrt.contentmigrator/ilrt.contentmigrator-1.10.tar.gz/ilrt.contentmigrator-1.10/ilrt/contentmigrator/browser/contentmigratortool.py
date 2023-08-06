from Globals import InitializeClass
from datetime import datetime
import os
from StringIO import StringIO
from csv import reader
from ConfigParser import ConfigParser

from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import getToolByName, UniqueObject
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFPlone.interfaces import IPloneBaseTool
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from zope.interface import implements
from zope.component import createObject
from zope.component import getUtility
from Products.Five.browser import BrowserView
from plone.memoize.compress import xhtml_compress
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.component import getUtility
from zope.component import queryAdapter, getAdapter
from Products.CMFCore.interfaces import ISiteRoot

from Products.GenericSetup.interfaces import IFilesystemImporter, IContentFactory
from Products.GenericSetup.interfaces import IINIAware, ISetupTool
from Products.GenericSetup.context import DirectoryImportContext
from Products.GenericSetup.utils import _resolveDottedName
# from Products.GenericSetup.content import FolderishExporterImporter

from ilrt.contentmigrator.browser.interfaces import IContentMigratorTool
from ilrt.contentmigrator.exportimport.content import importSiteStructure
from ilrt.contentmigrator.ContentMigrator.config import SEPARATOR, PROPS, ALLPROPS

from ilrt.contentmigrator.ContentMigrator.ContentExporter import ContentExporter
from ilrt.contentmigrator.ContentMigrator.interfaces import IContentExporterTool

MIGRATOR_TOOL_TYPE = "Content Migrator Tool"
MIGRATOR_TOOL_ID = "portal_setupcontent"

class ContentMigratorView(BrowserView):
    ''' This allows for zcml config of the management screens for the tool '''

class ContentMigratorTool(UniqueObject, SimpleItem, PloneBaseTool):
    """
    Tool to run a generic setup import and export with the following extra features

      - Populate binary content formats and archetypes if matching ones are found. 
      - Use Marshall's RFC822 marshaller to extract and apply the properties data.
      - Apply workflow state transitions.
    """

    implements(IPloneBaseTool, IContentMigratorTool, 
               IFilesystemImporter, IContentExporterTool)
    toolicon = 'tool.png'
    id = MIGRATOR_TOOL_ID
    meta_type = MIGRATOR_TOOL_TYPE
    title = "Content Migrator Tool"
    manage_import = PageTemplateFile(os.path.join('templates','importContentMigrator.pt'),globals())
    manage_export = PageTemplateFile(os.path.join('templates','exportContentMigrator.pt'),globals())

    def __init__(self):
        """ Set default context and start log """
        self.context_id = 'profile-ilrt.contentmigrator:import'
        self.import_context = None
        self.impout = []
        self.expout = []

    

    def manage_options(self):
        """ Builds a zope2 style menu from the zope3 configure.zcml one
            NB: Beware an empty tuple causes inaccurate security error """
        if getattr(self,'options',()) == ():
            zope2menu = []
            menu = getUtility(IBrowserMenu, name='contentmigrator_options')
            try:
                for item in menu.getMenuItems(self,getattr(self,'REQUEST',{})):
                    zope2menu.append({'label':item['title'],
                                 'action':str(item['action'])})
            except:
                pass
            self.options = tuple(zope2menu)
        return self.options

    def editContext(self, **kwargs):
        """ Update locale for import """
        request = getattr(self,'REQUEST',{})
        context_id = kwargs.get('context_id',
                                request.get('context_id',
                                            'profile-ilrt.contentmigrator:import'))
        reindex = kwargs.get('reindex',request.get('reindex','item')) 
        if context_id:
            gstool = getToolByName(self, 'portal_setup')
            self.context_id = context_id
            self.import_context = gstool._getImportContext(context_id)
            self.import_context.REQUEST['context_id'] = context_id
            self.import_context.REQUEST['reindex'] = reindex
                    
    def manage_runImport(self, root='/'):
        """ Run the import """
        request = getattr(self,'REQUEST',{})
        self.editContext()
        if self.import_context:
            newroot = request.get('root','') or root
            if newroot:
                self.root = newroot
            if not self.root:
                self.root = '/'
            self.impout = importSiteStructure(self.import_context, self.root)
        else:
            self.impout = ['Failed to set import context so no import was run',]
        if hasattr(request, 'RESPONSE'):
            request.RESPONSE.redirect('@@manage_import')

    def manage_runExport(self, root='/'):
        """ Run the export """
        request = getattr(self,'request',getattr(self,'REQUEST',{}))
        root = request.get('root','')
        users = request.get('exportusers',None)
        format = request.get('format', 'CSV')
        exp = ContentExporter()
        self.savepath = exp.get_var_path()
        if root:
            self.expout = ['Running export']
            expout = exp.export(root=root,
                             portal=getUtility(ISiteRoot),
                             users=users,
                             format=format,
                             request=request)
            if expout:
                self.expout.extend(expout)
            else:
                self.expout = ['Couldnt run export']
        if hasattr(request, 'RESPONSE'):
            request.RESPONSE.redirect('@@manage_export')

    def getLog(self):
        """ Backwards compatible call to show both """
        log = self.getImportLog()
        log.extend(self.getExportLog())
        return log

    def getExportLog(self):
        """ return the expout log file of export actions """
        return getattr(self,'expout',['No log found',])

    def getImportLog(self):
        """ return the impout log file of import actions """
        return getattr(self,'impout',['No log found',])

        
InitializeClass(ContentMigratorTool)
