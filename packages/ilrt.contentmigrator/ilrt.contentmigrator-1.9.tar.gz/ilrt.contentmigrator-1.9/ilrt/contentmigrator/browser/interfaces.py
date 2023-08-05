from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer

class IContentMigratorTool(Interface):
    """Marker interface for the tool
    """

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """
