""" EEA Geotags Installer
"""
from setuptools import setup, find_packages
import os

NAME = 'eea.geotags'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(os.path.join(*PATH)).read().strip()

setup(name=NAME,
      version=VERSION,
      description=(
          "EEA Geotags package redefines the location field in Plone. "
          "Right now in Plone location field is a free text field. "
          "EEA Geotags lets you easy define locations using a map picker "
          "and http://geonames.org geographical database."),
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='eea geotags widget field zope plone',
      author=('Alin Voinea (Eaudeweb), '
              'Antonio De Marinis (EEA), '
              'European Environment Agency (EEA)'),
      author_email='webadmin@eea.europa.eu',
      url=('http://svn.eionet.europa.eu/projects/'
           'Zope/browser/trunk/eea.geotags'),
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['eea'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.ATVocabularyManager',
          'archetypes.schemaextender',
          'eea.jquery',
          'eea.alchemy',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
