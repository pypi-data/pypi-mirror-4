try:
    from Products.CMFCore.permissions import setDefaultRoles
except ImportError:
    from Products.CMFCore.CMFCorePermissions import setDefaultRoles
from Products.CMFCore import utils
from ContentExporter import ContentExporter
from AccessControl import ModuleSecurityInfo

tools = ( ContentExporter, )

ModuleSecurityInfo('Products.ContentExporter').declarePublic('wrapText')

def initialize(context):

    utils.ToolInit('Content Migrator Tool', tools=tools,
                   product_name='ContentMigrator', icon='tool.gif',
                   ).initialize(context)
