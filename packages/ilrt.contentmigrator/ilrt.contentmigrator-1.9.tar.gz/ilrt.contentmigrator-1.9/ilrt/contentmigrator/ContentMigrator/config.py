SEPARATOR = "\n  "
# FOLDERS = ['Folder','Plone Folder','Large Plone Folder','Plone Memberdata Tool']
# Basic Plone or Zope properties and related methods (ie. doesnt require Archetypes) 
# NB: Nearly all these mappings actually equate to naming conventions -
# e.g. drop the underscore and camel case for the accessor but explicit mapping
# is quicker and better than guessing the accessor name!
PROPS = {}
PROPS['string'] = { 'id':'getId',
                    'title':'Title',
                    'description':'Description',
                    'language':'Language',
                    'rights':'Rights',
                    'Content-Type':'Format'
                   }

PROPS['date'] = {'effectiveDate':'EffectiveDate',
                 'expirationDate':'ExpirationDate',
                 'creation_date':'CreationDate',
                 'modification_date':'ModificationDate',
                 }

# Custom pre-Plone 2 navigation hiding property
PROPS['boolean'] = {'excludeFromNav':'navigation_hidden'}

PROPS['list'] = {'subject':'Subject',
                 'contributors':'Contributors',
                }
PROPS['user'] = {'owner':'Creator',
                 'lasteditor':'LastEditor',
                 }
# Required default booleans for plone3 structure doc 
PROPS['fixed'] = {'allowDiscussion':False,
                  'excludeFromNav':False,
                  'presentation':False,
                  'tableContents':False,
                  }

ALLPROPS = ['text','remote_url']
for value in PROPS.values():
    ALLPROPS.extend(value.keys())

# Translate or exclude object types

TYPEMAP = {'Calendar Item':'Event',
           'Link':'Link',
           'Plone Site':'',
           }

# The AT props are lower cased for pulling out so 
# about getting camel case right doesnt matter 

NONATPROPS = {'Calendar Item':{'start_date':'startDate',
                               'end_date':'endDate',
                               'location':'location',
                               'contact_name':'contactName',
                               'contact_email':'contactEmail',
                               'contact_phone':'contactPhone',
                               'event_url':'eventUrl'},
              'Link':{'remote_url':'remoteUrl'}     
              }

#Used to encode content written to text files,
#when characters are not within the ascii character range
DEFAULT_ENCODING='utf8'
