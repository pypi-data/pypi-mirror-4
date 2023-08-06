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
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
"""Setup for zope.apidoc package
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = 'zope.apidoc',
    version = '1.0.0',
    author = 'Zope Corporation and Contributors',
    author_email = 'zope-dev@zope.org',
    description = 'API Documentation and Component Inspection for Zope 3',
    long_description=(
        read('README.txt')
        + '\n\n.. contents::\n\n' +
        read('src', 'zope', 'apidoc', 'README.txt')
        + '\n\n' +
        read('src', 'zope', 'apidoc', 'component.txt')
        + '\n\n' +
        read('src', 'zope', 'apidoc', 'interface.txt')
        + '\n\n' +
        read('src', 'zope', 'apidoc', 'presentation.txt')
        + '\n\n' +
        read('src', 'zope', 'apidoc', 'utilities.txt')
        + '\n\n' +
        read('src', 'zope', 'apidoc', 'classregistry.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 api documentation",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        #'Programming Language :: Python :: 3',
        #'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://pypi.python.org/pypi/zope.apidoc',
    packages = find_packages('src'),
    package_dir = {'':'src'},
    namespace_packages = ['zope'],
    install_requires = [
        'setuptools',
        'zope.annotation',
        'zope.app.renderer',
        'zope.browserpage',
        'zope.browserresource',
        'zope.cachedescriptors',
        'zope.component',
        'zope.container',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.location',
        'zope.publisher',
        'zope.schema',
        'zope.security',
        'zope.traversing',
        ],
      extras_require = dict(
          test=[
            'zope.testing',
            ],
          ),
    include_package_data = True,
    tests_require=['zope.testing'],
    test_suite='zope.apidoc.tests.test_suite',
    zip_safe = False,
    )
