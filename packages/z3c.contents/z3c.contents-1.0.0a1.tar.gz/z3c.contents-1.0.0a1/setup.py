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
"""
$Id:$
"""

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='z3c.contents',
    version='1.0.0a1',
    author = "Roger Ineichen and the Zope Community",
    author_email = "zope3-dev@zope.org",
    description = "Container management page based on z3c.form and z3c.table for Zope3",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 z3c container manegement table contents",
    classifiers = [
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
    url = 'http://cheeseshop.python.org/pypi/z3c.contents',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        test = [
            'lxml',
            'z3c.macro',
            'z3c.layer.ready2go',
            'z3c.table',
            'zope.testing',
            'zope.tal >= 4.0.0a1', # attribute order changes
            ],
        ftest = [
            'z3c.etestbrowser',
            'zope.app.component',
            'zope.browserpage',
            'zope.app.securitypolicy',
            'zope.app.testing',
            ],
        ),
    install_requires = [
        'setuptools',
        'z3c.form',
        'z3c.formui',
        'z3c.table',
        'z3c.template',
        'zope.annotation',
        'zope.component',
        'zope.container',
        'zope.copypastemove',
        'zope.exceptions',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.index',
        'zope.interface',
        'zope.publisher',
        'zope.schema',
        'zope.security',
        'zope.traversing',
        ],
    test_suite='z3c.contents.tests.test_suite',
    zip_safe = False,
)
