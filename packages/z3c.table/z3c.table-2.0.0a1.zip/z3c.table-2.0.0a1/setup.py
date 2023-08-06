##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Setup
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name='z3c.table',
    version='2.0.0a1',
    author = "Stephan Richter, Roger Ineichen and the Zope Community",
    author_email = "zope-dev@zope.org",
    description = "Modular table rendering implementation for Zope3",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('src', 'z3c', 'table', 'README.txt')
        + '\n\n' +
        read('src', 'z3c', 'table', 'sort.txt')
        + '\n\n' +
        read('src', 'z3c', 'table', 'batch.txt')
        + '\n\n' +
        read('src', 'z3c', 'table', 'sequence.txt')
        + '\n\n' +
        read('src', 'z3c', 'table', 'column.txt')
        + '\n\n' +
        read('src', 'z3c', 'table', 'miscellaneous.txt')
        + '\n\n' +
        read('CHANGES.txt')),
    license="ZPL 2.1",
    keywords="zope3 z3c table content provider",
    classifiers=[
        'Development Status :: 4 - Beta',
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
    url='http://pypi.python.org/pypi/z3c.table',
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'},
    namespace_packages=['z3c'],
    extras_require=dict(
        test=[
            'zope.publisher',
            'zope.testing',
            'zope.container',
            'zope.site',
            ],
        ),
    install_requires=[
        'setuptools',
        'z3c.batching>=1.1.0',
        'zope.component',
        'zope.contentprovider',
        'zope.dublincore',
        'zope.i18nmessageid',
        'zope.i18n',
        'zope.interface',
        'zope.location',
        'zope.schema',
        'zope.security',
        'zope.traversing',
        ],
    test_suite='z3c.table.tests.test_suite',
    zip_safe=False,
)
