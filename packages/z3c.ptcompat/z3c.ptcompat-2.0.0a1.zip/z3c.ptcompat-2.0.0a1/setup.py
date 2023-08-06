##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED 'AS IS' AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(name='z3c.ptcompat',
      version='2.0.0a1',
      description='Zope-compatible page template engine based on Chameleon.',
      long_description=(
        '.. contents::\n\n' +
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
      classifiers=[
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
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: Plone',
        'Framework :: Zope2',
        'Framework :: Zope3',
        ],
      keywords='zpt template zope',
      url='http://pypi.python.org/pypi/z3c.ptcompat',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      license='ZPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'z3c.pt >= 2.1',
          'zope.pagetemplate >= 3.6.2',
          'zope.traversing',
          ],
      extras_require=dict(
          test=[
            'zope.testing',
            'zope.configuration'],
      ),
      tests_require=[
        'zope.testing',
        'zope.configuration'],
      test_suite='z3c.ptcompat.tests.test_suite',
      )
