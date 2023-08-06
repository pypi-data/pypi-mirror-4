from types import StringType, ListType, TupleType
from DateTime import DateTime
from ilrt.contentmigrator.ContentMigrator.config import SEPARATOR

# Archetype field type conversion method dictionary

def dummy(value):
    return None

def doboolean(value):
    if value and str(value) not in ('None','False'):
        return True
    else:
        return False

def dointeger(value):
    try:
        return int(value)
    except:
        return 0

def dofloat(value):
    try:
        return float(value)
    except:
        return 0

def dodatetime(value):
    if value:
        try:
            return DateTime(value)
        except:
            return None
    else:
        return None
    
def dotext(value):
    value = str(value).replace("\r", "")
    if value.endswith("\n"):
        value = value[:-2]
    return value.replace(SEPARATOR,"\n")

def dolines(value):
    return value.split("\n")

atconvert = {'computed':dummy, 'text':dotext, 'string':dotext, 
             'boolean':doboolean,'datetime':dodatetime,'lines':dolines,
             'integer':dointeger, 'float':dofloat, 'fixedpoint':dofloat}

