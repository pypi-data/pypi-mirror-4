""" EEA Faceted Inheritance Installer
"""
from setuptools import setup, find_packages
import os
from os.path import join

NAME = 'eea.faceted.inheritance'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(join(*PATH)).read().strip()

setup(name=NAME,
      version=VERSION,
      description=("EEA Faceted Navigation extension that allow a faceted "
                   "navigable object to inherit faceted configuration from "
                   "another faceted navigable object."),
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='eea faceted navigation inheritance plone zope python',
      author='Alin Voinea',
      author_email='alin@eaudeweb.ro',
      url='http://eggrepo.eea.europa.eu/simple',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['eea', 'eea.faceted'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'eea.facetednavigation',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
