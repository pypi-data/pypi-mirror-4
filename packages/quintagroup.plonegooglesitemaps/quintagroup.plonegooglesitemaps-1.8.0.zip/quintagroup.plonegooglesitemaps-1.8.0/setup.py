# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '1.8.0'

tests_require = ['zope.testing',
                 'collective.testcaselayer']

setup(name='quintagroup.plonegooglesitemaps',
      version=version,
      description="Allows Plone websites to get better visibility for "
                  "Google search engine",
      long_description=open("README.txt").read() + "\n" +
           open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
      ],
      keywords='plone google sitemap quintagroup search engine',
      author='Quintagroup',
      author_email='info@quintagroup.com',
      url='http://svn.quintagroup.com/products/'
          'quintagroup.plonegooglesitemaps',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quintagroup'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.browserlayer',
          'quintagroup.canonicalpath>=0.7',
          'quintagroup.catalogupdater',
          'archetypes.schemaextender',
          # -*- Extra requirements: -*-
      ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
