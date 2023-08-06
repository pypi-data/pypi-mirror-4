##############################################################################
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
"""Setup for z3c.batching package

$Id: setup.py 129785 2013-02-25 12:26:13Z alga $
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as f:
        return f.read()


setup(name='z3c.batching',
      version='2.0.0',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='Batching',
      long_description=(
          read('README.txt')
          + '\n\n'
          + '======================\n'
          + 'Detailed Documentation\n'
          + '======================\n'
          + '\n\n'
          + read('src', 'z3c', 'batching', 'README.txt')
          + '\n\n'
          + read('src', 'z3c', 'batching', 'subset.txt')
          + '\n\n'
          + read('CHANGES.txt')),
      keywords="zope3 batching",
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
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      url='http://pypi.python.org/pypi/z3c.batching',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['z3c'],
      install_requires=['setuptools',
                        'zope.interface',
                        'zope.schema',
                        ],
      include_package_data=True,
      test_suite='z3c.batching.tests.test_suite',
      zip_safe=False,
      )
