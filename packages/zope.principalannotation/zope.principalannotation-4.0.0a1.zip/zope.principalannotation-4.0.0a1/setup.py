##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Setup for zope.principalannotation package
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.principalannotation',
      version='4.0.0a1',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      description='Annotations for Zope Principals',
      long_description=(
          read('src', 'zope', 'principalannotation', 'README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope security principal annotation",
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      url='http://pypi.python.org/pypi/zope.principalannotation',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope'],
      extras_require = dict(
        test=['zope.testing', 'zope.site[test]'],
        docs=['z3c.recipe.sphinxdoc',]),
      install_requires=[
        'persistent',
        'setuptools',
        'zope.annotation',
        'zope.component',
        'zope.interface',
        'zope.location',
        'zope.security',
        'zope.site',
        ],
      tests_require=['zope.testing', 'zope.site[test]'],
      test_suite='zope.principalannotation.tests.test_suite',
      include_package_data = True,
      zip_safe = False,
      )
