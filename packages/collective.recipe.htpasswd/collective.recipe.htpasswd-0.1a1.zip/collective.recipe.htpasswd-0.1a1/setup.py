# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.recipe.htpasswd
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1a1'

long_description = (
    read('README.rst')
    + '\n' +
    #'Detailed Documentation\n'
    #'**********************\n'
    #+ '\n' +
    #read('src', 'collective', 'recipe', 'htpasswd', 'README.txt')
    #+ '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('docs', 'CONTRIBUTORS.rst')
    + '\n' +
    'History\n'
    '**************\n'
    + '\n' +
    read('docs', 'HISTORY.rst')
    + '\n' +
   'Download\n'
    '********\n')

entry_point = 'collective.recipe.htpasswd:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require = ['zope.testing', 'zc.buildout']

setup(name='collective.recipe.htpasswd',
      version=version,
      description="Buildout recipe for create and update the flat-files used to store usernames and password for basic authentication of HTTP users",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='buildout, recipe, htpasswd, password',
      author='Juan A. Diaz',
      author_email='nueces@ravvit.net',
      url='http://github.com/nueces/collective.recipe.htpasswd',
      license='GPL',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['collective', 'collective.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['zc.buildout',
                        'setuptools',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='collective.recipe.htpasswd.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
