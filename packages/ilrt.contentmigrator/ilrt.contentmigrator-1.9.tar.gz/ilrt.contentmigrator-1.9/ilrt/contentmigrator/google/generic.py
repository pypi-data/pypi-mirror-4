import os
SKIPPED_FILES = ('CVS', '.svn', '_svn', '_darcs')
SKIPPED_SUFFIXES = ('~',)

class ShellImportContext():
    """ From Products.GenericSetup.DirectoryImportContext 
        basic file system wrapper methods 
        for a plone / zope export folder (without zope or plone)
    """ 

    def __init__( self, profile_path):
        self._profile_path = profile_path

    def openDataFile( self, filename, subdir=None ):
        if subdir is None:
            full_path = os.path.join( self._profile_path, filename )
        else:
            full_path = os.path.join( self._profile_path, subdir, filename )

        if not os.path.exists( full_path ):
            return None

        return open( full_path, 'rb' )

    def readDataFile( self, filename, subdir=None ):
        result = None
        file = self.openDataFile( filename, subdir )
        if file is not None:
            result = file.read()
            file.close()
        return result

    def getLastModified( self, path ):
        full_path = os.path.join( self._profile_path, path )

        if not os.path.exists( full_path ):
            return None

        return DateTime( os.path.getmtime( full_path ) )

    def isDirectory( self, path ):
        full_path = os.path.join( self._profile_path, path )

        if not os.path.exists( full_path ):
            return None

        return os.path.isdir( full_path )

    def listDirectory(self, path, skip=SKIPPED_FILES,
                      skip_suffixes=SKIPPED_SUFFIXES):
        if path is None:
            path = ''

        full_path = os.path.join( self._profile_path, path )

        if not os.path.exists( full_path ) or not os.path.isdir( full_path ):
            return None

        names = []
        for name in os.listdir(full_path):
            if name in skip:
                continue
            if [s for s in skip_suffixes if name.endswith(s)]:
                continue
            names.append(name)

        return names
