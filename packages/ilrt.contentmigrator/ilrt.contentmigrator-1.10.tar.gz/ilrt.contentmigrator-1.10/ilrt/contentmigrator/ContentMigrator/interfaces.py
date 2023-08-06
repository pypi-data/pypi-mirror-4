try:
    from zope.interface import Interface
except ImportError:
    try:
        # Old inteface packages
        from Interface import Interface
    except ImportError:
        # Very old interface package
        from Interface import Base as Interface

class IContentExporterTool(Interface):
    """ Add a marker interface so that export class can be amalgamated into
        Plone3 or later tool
    """
