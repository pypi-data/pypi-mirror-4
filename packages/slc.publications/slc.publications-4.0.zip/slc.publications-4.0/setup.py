# -*- coding: utf-8 -*-
"""
This module contains the slc.publications package
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '4.0'

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n'
    )

setup(name='slc.publications',
      version=version,
      description="A content type to store and parse pdf publications",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "License :: OSI Approved :: European Union Public Licence 1.1 (EUPL 1.1)",
        ],
      keywords='plone content publications pdf parse metadata',
      author='Syslab.com GmbH',
      author_email='info@syslab.com',
      url='http://plone.org/products/slc.publications',
      license='GPL + EUPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['slc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'p4a.common',
          'p4a.z2utils',
          'p4a.subtyper',
          'archetypes.schemaextender',
          'z3c.jbot',
      ],
      extras_require={
          'test': [
              'zope.testing',
              'plone.app.blob',
          ],
      },
      test_suite='slc.publications.tests.test_docs.test_suite',
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )

