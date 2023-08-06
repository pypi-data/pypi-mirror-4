from StringIO import StringIO

def install(self):
    out = StringIO()

    #Add tool
    try:
        if not hasattr(self, 'portal_exportcontent'):
            addTool = self.manage_addProduct['ContentMigrator'].manage_addTool
            addTool('Content Migrator Tool')
    except:
         print >> out, "Failed to install tool"

    print >> out, "Installed of Content Migrator Tool complete."
    return out.getvalue()

def uninstall (self):

    """This method gets looked up by default and run before the other standard uninstall functions"""

    out = StringIO()

    #Should just work without any custom stuff here

    print >> out, "Removal of Content Migrator Tool complete."
    return out.getvalue()
