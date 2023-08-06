##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Setup for zope.preference package
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name = 'zope.preference',
      version='4.0.0a1',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='User Preferences Framework',
      long_description=(
          read('README.txt')
          + '\n\n' +
          '.. contents::\n\n' +
          read('src', 'zope', 'preference', 'README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "bluebream zope zope3 user preference",
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
          'Framework :: Zope3'],
      url='http://pypi.python.org/pypi/zope.preference',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope'],
      extras_require=dict(test=[
          'zope.site',
          'zope.testing',
          ]),
      install_requires = [
        'setuptools',
        'BTrees',
        'zope.annotation',
        'zope.component >= 3.8.0',
        'zope.container',
        'zope.schema',
        'zope.security',
        'zope.traversing',
        ],
      tests_require = [
          'zope.site',
          'zope.testing',
          ],
      test_suite = 'zope.preference.tests.test_suite',
      include_package_data = True,
      zip_safe = False,
      )
