# Command line utility script to run import
#Products.CMFCore.interfaces import ISiteRoot
#from zope.component import getUtility

profile_id = "ilrt.contentmigrator:import"
portal = None

for item in app:
    if hasattr(item, 'getTypeInfo') and item.getTypeInfo().getId() == 'Plone Site':
        portal = item
        break
if portal:
    print 'Portal %s found' % portal.getId()
    importer = getattr(portal, 'portal_setupcontent')
    importer.editContext(context_id='profile-%s' % profile_id)
    setattr(importer,'REQUEST',{})
    importer.manage_runImport(root='/')
    out = getattr(importer,out)
    if out:
        for line in out:
            print line
else:
    print 'Portal not found'
