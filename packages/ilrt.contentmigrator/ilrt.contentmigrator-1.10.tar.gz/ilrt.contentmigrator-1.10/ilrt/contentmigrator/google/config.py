# Repeat export config here but modify for Google
DEFAULT_ENCODING='utf8'
SEPARATOR = "\n  "
FOLDERTYPES = ['filecabinet','webpage']
TYPEMAP = {#'announcementpage':'NewsFolder',
           'announcement':'News',
           'filecabinet':'Folder',
           'attachment':'File',
           'webpage':'Document'
           }
PROPS = {}
PROPS['string'] = { 'language':('language','en'),
                   }
PROPS['id'] = ['title','id']

PROPS['user'] = {'owner':'Creator',
                 'lasteditor':'LastEditor',
                 }
PROPS['fixed'] = {'allowDiscussion':'False',
                  'excludeFromNav':'False',
                  'presentation':'False',
                  'tableContents':'False',
                  'workflows': 'plone_workflow',
                  'states': 'published'
                  }
FIXMIME = {'jpe':'jpg', 'xlb':'xls' }
