# user,group and roles import
import os
from csv import reader
from ConfigParser import ConfigParser
from StringIO import StringIO
from OFS.Image import Image
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.plugins.exportimport import \
     ZODBUserManagerExportImport, ZODBRoleManagerExportImport, ZODBGroupManagerExportImport

PAS = {
       'source_groups':ZODBGroupManagerExportImport,
       'source_users':ZODBUserManagerExportImport,
       'portal_role_manager':ZODBRoleManagerExportImport
       }

def import_users(context):
    """ Run the PAS import for generic setup adapters
        Import users memberdata
    """
    out = []
    site = context.getSite()
    path = os.path.join('structure','acl_users')
    if context.isDirectory(path):
        for name in PAS.keys():
            out.append(pas_plugin(context, site, path, name))
    else:
        return out.append('No acl_users folder so user import skipped')
 
    path = os.path.join(path, 'portal_memberdata')
    objects = None
    if context.isDirectory(path):
        objects = context.readDataFile('.objects', path)
    if objects is None:
        return out.append('No member data found')

    stream = StringIO(objects)
    rowiter = reader(stream, 'excel')
    ours = filter(None, tuple(rowiter))
    user_ids = set([item[0] for item in ours])
    membership = getToolByName(site, 'portal_membership')
    memberdata = getToolByName(site, 'portal_memberdata')    
    i = 0
    for user_id in user_ids:
        member = membership.getMemberById(user_id)
        if member:
            meta = context.readDataFile(user_id, path)
            parser = ConfigParser()
            parser.readfp(StringIO(meta))
            metadict = parser.defaults()
            if metadict:
                member.setMemberProperties(metadict)
                i += 1
            #TODO: get portrait import working
            #for pictype in ['jpeg','jpg','gif','png']:
            #    picname = '%s.%s' % (user_id, pictype)
            #    pic = context.readDataFile(picname, path)
            #    if pic:
            #        img = Image(id=picname, file=pic, title=user_id)
            #        img.setImage(pic, 'image/%s' % pictype)
            #        memberdata._setPortrait(img, user_id)
            #        break
    out.append("Updated %d member's data" % i)
    return out

def pas_plugin(context, site, path, name):
    """ Run the PluggableAuthService imports """
    if not hasattr(site, 'acl_users'):
        return 'Site has no acl_users folder'
    plugin = getattr(site.acl_users, name, None)
    if plugin:
        adapter = PAS[name](plugin)
        try:
            adapter.import_(context, path, False)
        except KeyError, err:
            return '%s import not done due to %s' % (name,str(err))
        except:
            return '%s import failed due to parsing error' % name
        return 'Ran import of %s' % name
    return 'No PAS %s plugin found to run import' % name
    
