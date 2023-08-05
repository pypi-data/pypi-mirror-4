##############################################################################
#
# Copyright (c) 2012 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__version__ = '1.1'

import os

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

_boundary = '\n' + ('-' * 60) + '\n\n'

setup(name='dataflake.fakeldap',
      version=__version__,
      description='LDAP connection library',
      long_description=( read('README.txt') 
                       + "\n\nDownload\n========"
                       ),
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP",
        ],
      keywords='ldap ldapv3',
      author="Jens Vagelpohl",
      author_email="jens@dataflake.org",
      url="http://pypi.python.org/pypi/dataflake.fakeldap",
      license="ZPL 2.1",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['dataflake'],
      zip_safe=False,
      setup_requires=['setuptools-git'],
      install_requires=[
            'setuptools',
            'python-ldap',
            ],
      tests_require=['python-ldap'],
      test_suite='dataflake.fakeldap.tests',
      extras_require={ 'docs': [ 'sphinx'
                               , 'pkginfo'
                               , 'sphinx-pypi-upload'
                               , 'zc.rst2'
                               ]
                     , 'testing': ['nose', 'coverage']
                     },
      )

