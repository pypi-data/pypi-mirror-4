##############################################################################
#
# Copyright (c) 2006-2009 Zope Foundation and Contributors.
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
"""Setup for zope.ramcache package
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

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
    return unittest.TestSuite(suites)

setup(name = 'zope.ramcache',
      version='2.0.0',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      description='Zope RAM Cache',
      long_description=(
          read('README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope cache",
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: Implementation :: CPython',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          ],
      url='http://pypi.python.org/pypi/zope.ramcache',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope'],
      install_requires = [
          'persistent',
          'setuptools',
          'zope.interface',
          'zope.location',
          'zope.testing',
          ],
      tests_require = ['zope.testrunner'],
      test_suite = '__main__.alltests',
      include_package_data = True,
      zip_safe = False,
      )
