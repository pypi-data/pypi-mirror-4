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
"""Setup
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

TESTS_REQUIRE = [
    'zope.testing',
    'z3c.coverage',
    'z3c.form [test]',
    ]

setup (
    name='z3c.formwidget.ckeditor',
    version='2.0.0a1',
    author = "Stephan Richter and the Zope Community",
    author_email = "zope-dev@zope.org",
    description = "A CKEditor widget for text fields using z3c.form",
    long_description=(
        read('README.txt')
        + '\n\n' +
        'Detailed Documentation\n'
        '**********************'
        + '\n\n' +
        read('src', 'z3c', 'formwidget', 'ckeditor', 'README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 form widget ckeditor text",
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
    url = 'http://pypi.python.org/pypi/z3c.formwidget.ckeditor',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c', 'z3c.formwidget'],
    extras_require = dict(
        demo = [
            'ZConfig',
            'transaction',
            'waitress',
            'z3c.form',
            'z3c.formui',
            'z3c.layer.pagelet',
            'z3c.macro',
            'z3c.pagelet',
            'z3c.schema',
            'z3c.template',
            'zope.app.appsetup',
            'zope.app.http',
            'zope.app.wsgi',
            'zope.error',
            'zope.paste',
            'zope.principalregistry',
            'zope.publisher',
            'zope.securitypolicy',
            'zope.traversing',
            ],
        test = TESTS_REQUIRE,
        ),
    install_requires = [
        'setuptools',
        'simplejson',
        'six',
        'z3c.form',
        'zope.component',
        'zope.interface',
        'zope.schema',
        'zope.viewlet',
        ],
    tests_require=TESTS_REQUIRE,
    test_suite='z3c.menu.ready2go.tests.test_suite',
    zip_safe = False,
    )
