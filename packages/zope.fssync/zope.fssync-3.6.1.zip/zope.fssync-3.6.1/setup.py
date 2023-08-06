##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Setup for zope.fssync package

$Id: setup.py 130225 2013-05-02 10:47:27Z tlotze $
"""

import os

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.fssync',
      version='3.6.1',
      url='http://pypi.python.org/pypi/zope.fssync',
      license='ZPL 2.1',
      description="Filesystem synchronization utility for Zope 3.",
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description=(read('README.txt')
                        + '\n\n' +
                        read('src', 'zope', 'fssync', 'README.txt')
                        + '\n\n' +
                        read('CHANGES.txt')),
      keywords = "zope3 serialization synchronization",
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
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope',],
      tests_require = ['ZODB3', 'zope.testing', 'py'],
      extras_require={
          'test': ['zope.testing',
                   'py'],
          },
      install_requires = ['setuptools',
                          'zope.annotation',
                          'zope.component',
                          'zope.dottedname',
                          'zope.filerepresentation',
                          'zope.interface',
                          'zope.lifecycleevent',
                          'zope.location',
                          'zope.proxy',
                          'zope.traversing',
                          'zope.xmlpickle'],
      include_package_data = True,

      zip_safe = False,
      )
