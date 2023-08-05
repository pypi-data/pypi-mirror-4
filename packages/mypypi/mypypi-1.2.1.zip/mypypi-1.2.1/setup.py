##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
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

$Id:$
"""

import os
import sys
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup (
    name='mypypi',
    version='1.2.1',
    author = "Projekt01 GmbH, 6330 Cham, Switzerland",
    author_email = "dev@projekt01.ch",
    description = "My Python Package Index (Standalone Server)",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('INSTALL.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "python buildout package index server egg pypi mirror private",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://pypi.python.org/pypi/mypypi',
    packages = find_packages('src'),
    package_dir = {'':'src'},
    namespace_packages = [],
    extras_require = dict(
        test = [
            'z3c.testing',
            'zope.app.testing',
            'zope.testing',
            'zope.testbrowser',
            ],
        ),
    install_requires = [
        'setuptools',
        'docutils',
        'BeautifulSoup',
        'p01.accelerator',
        'p01.fsfile',
        'p01.fswidget',
        'p01.remote',
        'p01.tmp',
        'p01.zmi',
        'z3c.authenticator',
        'z3c.breadcrumb',
        'z3c.configurator',
        'z3c.form',
        'z3c.formui',
        'z3c.indexer',
        'z3c.layer.ready2go',
        'z3c.menu.ready2go',
        'z3c.schema',
        'z3c.table',
        'z3c.tabular',
        'z3c.template',
        'zope.annotation',
        'zope.app.appsetup',
        'zope.app.generations',
        'zope.app.publication',
        'zope.app.security',
        'zope.app.wsgi',
        'zope.authentication',
        'zope.component',
        'zope.container',
        'zope.contentprovider',
        'zope.event',
        'zope.exceptions',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.index',
        'zope.interface',
        'zope.intid',
        'zope.lifecycleevent',
        'zope.location',
        'zope.principalannotation',
        'zope.publisher',
        'zope.schema',
        'zope.security',
        'zope.securitypolicy',
        'zope.site',
        'zope.traversing',
        ],
    zip_safe = False,
    include_package_data = True,
    package_data = {'': ['*.txt', '*.cfg', '*.py', 'buildout.cfg'],},
    entry_points = """
        [paste.app_factory]
        main = mypypi.wsgi:application_factory
        """,
    )
