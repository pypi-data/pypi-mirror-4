from setuptools import setup, find_packages
import os

version = '1.9'

setup(name='ilrt.contentmigrator',
      version=version,
      description="Migrate old Plone or Google Sites content to current Plone 4",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("ilrt","contentmigrator","google","README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read() + "\n" +
                       open(os.path.join("docs", "TODO.txt")).read(),      
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Intended Audience :: Developers",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta"
        ],
      keywords='web zope plone migration setup release management workflow',
      author='Internet Development, ILRT, University of Bristol',
      author_email='internet-development@bris.ac.uk',
      url='http://bitbucket.org/edcrewe/ilrt.contentmigrator',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ilrt'],
      include_package_data=True,
      package_data = {'docs': ['*.txt', '*.rst']},
      zip_safe=False,
      install_requires=[
          'setuptools',
          'ilrt.migrationtool',
          'gdata'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

