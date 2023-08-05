import unittest
from Testing import ZopeTestCase as ztc
from ilrt.contentmigrator.tests import base

try: 
    # Plone 4 and higher 
    import plone.app.upgrade 
    PLONE_VERSION = 4 
except ImportError: 
    PLONE_VERSION = 3

def test_suite():
    if PLONE_VERSION == 4:
        return unittest.TestSuite([
           ztc.ZopeDocFileSuite(
                'tests/export.txt', package='ilrt.contentmigrator',
                test_class=base.BaseFunctionalTestCase),
            
           ztc.ZopeDocFileSuite(
                'tests/import.txt', package='ilrt.contentmigrator',
                test_class=base.BaseFunctionalTestCase),

            ztc.ZopeDocFileSuite(
                'tests/export_google.txt', package='ilrt.contentmigrator',
                test_class=base.BaseFunctionalTestCase),

           ztc.ZopeDocFileSuite(
                'tests/import_google.txt', package='ilrt.contentmigrator',
                test_class=base.BaseFunctionalTestCase),
            ])
    else:
        return unittest.TestSuite([
            ztc.ZopeDocFileSuite(
                'tests/export3.txt', package='ilrt.contentmigrator',
                test_class=base.BaseFunctionalTestCase),

            ztc.ZopeDocFileSuite(
                'tests/import3.txt', package='ilrt.contentmigrator',
                test_class=base.BaseFunctionalTestCase),
            ])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
