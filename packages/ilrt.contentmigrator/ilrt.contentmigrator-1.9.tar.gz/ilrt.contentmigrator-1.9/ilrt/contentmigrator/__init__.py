# Extras above empty def initialize are to add an icon for the tool
from Products.CMFCore import utils
from ilrt.contentmigrator.browser.contentmigratortool import ContentMigratorTool

tools = (
            ContentMigratorTool,
        )

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    utils.ToolInit( 'Content Migrator Tool'
                              , tools=tools
                              , icon='tool.png'
                              ).initialize(context)
        
