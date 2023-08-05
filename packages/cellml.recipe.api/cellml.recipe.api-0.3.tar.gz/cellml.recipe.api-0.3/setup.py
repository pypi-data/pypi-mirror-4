# -*- coding: utf-8 -*-
"""
This module contains the tool of cellml.recipe.api
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.3'

long_description = (
    read('README.rst')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' + 
    read('CHANGES.rst')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('cellml', 'recipe', 'api', 'README.rst')
    + '\n' +
    'Contributors\n' 
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )
entry_point = 'cellml.recipe.api:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require=['zope.testing', 'zc.buildout']

setup(name='cellml.recipe.api',
      version=version,
      description="Recipe to call CMake to build CellML API and Python bindings",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)',
        ],
      keywords='cellml',
      author='Tommy Yu',
      author_email='tommy.yu@auckland.ac.nz',
      url='http://www.cellml.org/tools/api/',
      license='GPL/LGPL/MPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['cellml', 'cellml.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout',
                        # -*- Extra requirements: -*-
                        'zc.recipe.cmmi',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'cellml.recipe.api.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
