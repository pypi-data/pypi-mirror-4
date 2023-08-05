# -*- coding: utf-8 -*-
"""
This module contains the tool of ageliaco.recipe.csvconfig
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.6'

long_description = (
    read('README.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('ageliaco', 'recipe', 'csvconfig', 'README.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
   'Download\n'
    '********\n')

entry_point = 'ageliaco.recipe.csvconfig:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require = ['zope.testing', 'zc.buildout']

setup(name='ageliaco.recipe.csvconfig',
      version=version,
      description="Use a CSV file to populate buildout templates",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Zope Public License',
        ],
      keywords='buildout recipe',
      author='Serge Renfer',
      author_email='serge.renfer@gmail.com',
      url='https://github.com/renfers/ageliaco.recipe.csvconfig',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ageliaco', 'ageliaco.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout'
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='ageliaco.recipe.csvconfig.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
