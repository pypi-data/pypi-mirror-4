###############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup for z3c.traverser package
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    data = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    return data + "\n\n"

def alltests():
    import os
    import sys
    import unittest
    # use the zope.testrunner machinery to find all the
    # test suites we've put under ourselves
    import zope.testrunner.find
    import zope.testrunner.options
    here = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
    args = sys.argv[:]
    defaults = ["--test-path", here]
    options = zope.testrunner.options.get_options(args, defaults)
    suites = list(zope.testrunner.find.find_suites(options))
    # Filter out all tests with layers.
    import zope.testrunner.eggsupport
    suites = [zope.testrunner.eggsupport.skipLayers(suite)
              for suite in suites]
    return unittest.TestSuite(suites)

TESTS_REQUIRE = [
    'WebTest',
    'zope.app.appsetup',
    'zope.app.publication',
    'zope.app.wsgi',
    'zope.authentication',
    'zope.browserpage',
    'zope.container',
    'zope.error',
    'zope.principalregistry',
    'zope.security',
    'zope.site',
    'zope.testbrowser',
    'zope.testing',
    'zope.testrunner>=4.3.1',
    ]

setup(name='z3c.traverser',
      version='1.0.0a1',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='Pluggable Traversers And URL handling utilities',
      long_description=(
          read('README.txt') +
          '.. contents::\n\n' +
          read('CHANGES.txt') +
          read('src', 'z3c', 'traverser', 'README.txt') +
          read('src', 'z3c', 'traverser', 'namespace.txt') +
          read('src', 'z3c', 'traverser', 'viewlet', 'README.txt') +
          read('src', 'z3c', 'traverser', 'viewlet', 'BROWSER.txt') +
          read('src', 'z3c', 'traverser', 'stackinfo', 'README.txt') +
          read('src', 'z3c', 'traverser', 'stackinfo', 'BROWSER.txt')
          ),
      keywords = "zope3 traverser pluggable plugin viewlet",
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      url='http://pypi.python.org/pypi/z3c.traverser',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['z3c'],
      extras_require = dict(
          test = TESTS_REQUIRE,
          ),
      setup_requires=[
        'zope.testrunner>=4.3.1',
        'eggtestinfo',
        ],
      install_requires=(
          'setuptools',
          'zope.component',
          'zope.contentprovider',
          'zope.interface',
          'zope.publisher',
          'zope.traversing',
          'zope.viewlet',
          'zope.testrunner',
          ),
      tests_require=TESTS_REQUIRE,
      test_suite='__main__.alltests',
      include_package_data = True,
      zip_safe = False,
      )
