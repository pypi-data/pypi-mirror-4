# -*- coding: utf-8 -*-
"""
This module contains the slc.seminarportal package
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.4.5'

long_description = (
    read('README.txt')
    + '\n' +
    read('docs/CHANGES.txt')
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n'
    )

setup(name='slc.seminarportal',
      version=version,
      description="A Seminar and Conference websites built on Plone",
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
      keywords='seminar section subsite',
      author='Syslab.com GmbH',
      author_email='info@syslab.com',
      url='http://pypi.python.org/pypi/slc.seminarportal/',
      license='GPL + EUPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['slc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
            'setuptools',
            'Products.Relations',
            'Products.ATReferenceBrowserWidget',
            'Products.LinguaPlone',
            'collective.orderedmultiselectwidget',
      ],
      extras_require={
          'test': [
              'plone.app.testing',
              'mock',
          ],
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
