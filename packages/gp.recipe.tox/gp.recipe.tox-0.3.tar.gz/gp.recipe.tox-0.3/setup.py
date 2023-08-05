# -*- coding: utf-8 -*-
"""
This module contains the tool of gp.recipe.tox
"""
from setuptools import setup, find_packages


def read(name):
    try:
        return open(name).read()
    except:
        return ''

version = '0.3'

long_description = (
    read('README.rst')
    + '\n' +
    read('CHANGES.txt'))

entry_point = 'gp.recipe.tox:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require = ['zope.testing', 'zc.buildout']

setup(name='gp.recipe.tox',
      version=version,
      description="use buildout with tox",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        ],
      keywords='tox buildout',
      author='Gael Pasgrimaud',
      author_email='gael@gawel.org',
      url='https://github.com/gawel/gp.recipe.tox',
      license='gpl',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['gp', 'gp.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout',
                        'zc.recipe.egg',
                        'virtualenv',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='gp.recipe.tox.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
