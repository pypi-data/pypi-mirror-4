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
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import md5
import os
import shutil
import urllib2
import StringIO

import mypypi.api

import p01.tmp.storage
import p01.fsfile.storage

from zope.testing import doctest
from zope.app.testing import setup
from zope.app.testing import functional

###############################################################################
#
# Test Component
#
###############################################################################

#put here some testing globals
#those will be filled by default with good values
#it will be real easy to mess these up in testcases to produce some failures

Z3C_FORM_VERSIONS = ['1.9.0', '1.8.2', '1.8.1', '1.8.0', '1.7.0', '1.6.0',
                    '1.5.0b1', '1.5.0', '1.4.0b1', '1.4.0', '1.3.0',
                    '1.2.0', '1.1.0', '1.0c2', '1.0c1', '1.0.0']

Z3C_AUTH_VERSIONS = ['0.5.0']

WSGI_INTERCEPT_VERSIONS = ['0.1', '0.2', '0.3']

PACKAGES = {
    'z3c.form': Z3C_FORM_VERSIONS,
    'z3c.authenticator': Z3C_AUTH_VERSIONS,
    'wsgi_intercept': WSGI_INTERCEPT_VERSIONS,
}

URLS = {}
MD5S = {}

def addUrls(versions, package):
    global URLS, MD5S
    for version in versions:
        url = 'http://pypi.python.org/packages/source/%s/%s/%s-%s.tar.gz' % (
            package[0], package, package, version )
        content = 'TGZ--PACKAGE--%s--%s--ENDTGZ' % (package.upper(), version)
        URLS[url] = content

        name = '%s-%s' % (package, version)
        MD5S[name] = (len(content), md5.md5(content).hexdigest())

addUrls(Z3C_FORM_VERSIONS, 'z3c.form')
addUrls(Z3C_AUTH_VERSIONS, 'z3c.authenticator')
addUrls(WSGI_INTERCEPT_VERSIONS, 'wsgi_intercept')

def fakeUrlOpener(url):
    #use this method instead of urllib2.urlopen
    #we can return a StringIO or raise urllib2.HTTPError
    try:
        return StringIO.StringIO(URLS[url])
    except KeyError:
        #last two parameters are a blind guess
        raise urllib2.HTTPError(url, 404, 'Not found', {}, None)

class FakeXMLRPCPYPI(object):
    """Fake XMLRPC PYPI server API."""

    def __init__(self, url, transport=None, allow_none=0):
        self.url = url
        self.transport = transport

    def list_packages(self):
        """Retrieve a list of the package names registered with the package
        index.

        Returns a list of name strings.
        """
        return list(PACKAGES.keys())

    def package_releases(self, packageName, show_hidden=False):
        """Retrieve a list of the releases registered for the given package
        name.

        Returns a list of version strings.
        """
        try:
            package = PACKAGES[packageName]

            if show_hidden:
                return package
            else:
                return [package[0]]
        except KeyError:
            return []

    def release_urls(self, packageName, version):
        """Retrieve a list of download URLs for the given package release.

        Returns a list of dicts with the following keys:

        - url

        - packagetype ('sdist', 'bdist', etc)

        - filename

        - size

        - md5_digest

        - downloads

        - has_sig

        - python_version (required version, or 'source', or 'any')

        - comment_text

        """
        if packageName == 'z3c.form':
            if version in Z3C_FORM_VERSIONS:
                md5 = MD5S['%s-%s' % (packageName, version)]
                return [
                    {'has_sig': False,
                     'comment_text': '',
                     'python_version': 'source',
                     'url': 'http://pypi.python.org/packages/source/z/z3c.form/z3c.form-%s.tar.gz' % version,
                     'md5_digest': md5[1],
                     'downloads': 458,
                     'filename': 'z3c.form-%s.tar.gz' % version,
                     'packagetype': 'sdist',
                     'size': md5[0]}]

        if packageName == 'z3c.authenticator':
            if version in Z3C_AUTH_VERSIONS:
                md5 = MD5S['%s-%s' % (packageName, version)]
                return [
                    {'has_sig': False,
                     'comment_text': '',
                     'python_version': 'source',
                     'url': 'http://pypi.python.org/packages/source/z/z3c.authenticator/z3c.authenticator-%s.tar.gz' % version,
                     'md5_digest': md5[1],
                     'downloads': 458,
                     'filename': 'z3c.authenticator-%s.tar.gz' % version,
                     'packagetype': 'sdist',
                     'size': md5[0]}]

        if packageName == 'wsgi_intercept':
            if version in WSGI_INTERCEPT_VERSIONS:
                md5 = MD5S['%s-%s' % (packageName, version)]
                return [
                    {'has_sig': False,
                     'comment_text': '',
                     'python_version': 'source',
                     'url': 'http://pypi.python.org/packages/source/w/wsgi_intercept/wsgi_intercept-%s.tar.gz' % version,
                     'md5_digest': md5[1],
                     'downloads': 23,
                     'filename': 'wsgi_intercept-%s.tar.gz' % version,
                     'packagetype': 'sdist',
                     'size': md5[0]}]

        raise KeyError("Testdata not supported for '%s' version '%s'" % (
            packageName, version))

    def release_data(self, packageName, version):
        if packageName == 'z3c.authenticator':
            if version in Z3C_AUTH_VERSIONS:
                return {
                    'maintainer': None,
                    'maintainer_email': None,
                    'cheesecake_code_kwalitee_id': None,
                    'keywords': 'zope3 z3c json rpc tree',
                    'author': 'Roger Ineichen and the Zope Community',
                    'author_email': 'zope3-dev@zope.org',
                    'download_url': 'UNKNOWN',
                    'platform': 'UNKNOWN',
                    'version': version,
                    'obsoletes': [],
                    'provides': [],
                    'cheesecake_documentation_id': None,
                    '_pypi_hidden': 1,
                    'description': "This package provides an --- Release",
                    '_pypi_ordering': 10,
                    'classifiers': ['Development Status :: 4 - Beta',
                        'Environment :: Web Environment',
                        'Framework :: Zope3',
                        'Intended Audience :: Developers',
                        'License :: OSI Approved :: Zope Public License',
                        'Natural Language :: English',
                        'Operating System :: OS Independent',
                        'Programming Language :: Python',
                        'Topic :: Internet :: WWW/HTTP'],
                    'name': 'z3c.authenticator',
                    'license': 'ZPL 2.1',
                    'summary': 'IAuthentication implementation for for Zope3',
                    'home_page': 'http://cheeseshop.python.org/pypi/z3c.authenticator',
                    'stable_version': None,
                    'requires': [],
                    'cheesecake_installability_id': None}

        if packageName == 'z3c.form':
            if version in Z3C_FORM_VERSIONS:
                return {
                    'maintainer': None,
                    'maintainer_email': None,
                    'cheesecake_code_kwalitee_id': None,
                    'keywords': 'zope3 form widget',
                    'author': 'Stephan Richter, Roger Ineichen and the Zope Community <zope-dev at zope org>',
                    'author_email': 'zope3-dev@zope.org',
                    'download_url': 'UNKNOWN',
                    'platform': 'UNKNOWN',
                    'version': version,
                    'obsoletes': [],
                    'provides': [],
                    'cheesecake_documentation_id': None,
                    '_pypi_hidden': 1,
                    'description': "This package provides an --- Release",
                    '_pypi_ordering': 10,
                    'classifiers': ['Development Status :: 5 - Production/Stable',
                        'Environment :: Web Environment',
                        'Framework :: Zope3',
                        'Intended Audience :: Developers',
                        'License :: OSI Approved :: Zope Public License',
                        'Natural Language :: English',
                        'Operating System :: OS Independent',
                        'Programming Language :: Python',
                        'Topic :: Internet :: WWW/HTTP'],
                    'name': 'z3c.form',
                    'license': 'ZPL 2.1',
                    'summary': 'IAuthentication implementation for for Zope3',
                    'home_page': 'http://cheeseshop.python.org/pypi/z3c.authenticator',
                    'stable_version': None,
                    'requires': [],
                    'cheesecake_installability_id': None}

        if packageName == 'wsgi_intercept':
            if version in WSGI_INTERCEPT_VERSIONS:
                return {
                    'maintainer': None,
                    'maintainer_email': None,
                    'cheesecake_code_kwalitee_id': None,
                    'keywords': '',
                    'author': 'Titus Brown, Kumar McMillan',
                    'author_email': 'kumar.mcmillan@gmail.com',
                    'download_url': 'UNKNOWN',
                    'platform': 'UNKNOWN',
                    'version': version,
                    'obsoletes': [],
                    'provides': [],
                    'cheesecake_documentation_id': None,
                    '_pypi_hidden': 1,
                    'description': "Introduction",
                    '_pypi_ordering': 10,
                    'classifiers': [],
                    'name': packageName,
                    'license': 'MIT License',
                    'summary': 'installs a WSGI application in place of a real URI for testing.',
                    'home_page': 'http://code.google.com/p/wsgi_intercept/',
                    'stable_version': None,
                    'requires': [],
                    'cheesecake_installability_id': None}


        raise KeyError("Testdata not supported for '%s' version '%s'" % (
            packageName, version))

    def search(self, spec, operator='and'):
        """Search the package database using the indicated search spec.

        The spec may include any of the keywords described in the above list
        (except 'stable_version' and 'classifiers'), for example:

        {'description': 'spam'}

        will search description fields. Within the spec, a field's value can
        be a string or a list of strings (the values within the list are
        combined with an OR), for example:

        {'name': ['foo', 'bar']}.

        Arguments for different fields are combined using either "and"
        (the default) or "or". Example:

        search({'name': 'foo', 'description': 'bar'}, 'or').

        The results are returned as a list of dicts:

        {'name': package name,
         'version': package release version,
         'summary': package release summary}

         """
        if spec == {'name': 'z3c.form', 'version': '1.9.0'} and \
            operator == 'and':
            return [
                {'_pypi_ordering': 115,
                 'version': '1.9.0',
                 'name': 'z3c.form',
                 'summary': 'An advanced form and widget framework for Zope 3'
                 }]

        raise KeyError("Testdata not supported for spec '%s' operator '%s'" % (
            spec, operator))

    def changelog(self, since):
        """Retrieve a list of four-tuples (name, version, timestamp, action)
        since the given timestamp. All timestamps are UTC values. The argument
        is a UTC integer seconds since the epoch.
        """
        return   [
            ['pypi', '2005-08-01', 1198792881, 'update home_page, classifiers'],
            ['pypi', '2005-08-01', 1198792910, 'update summary, classifiers'],
            ['zope.app.publisher', '3.5.0a4', 1198850101,
                'add source file zope.app.publisher-3.5.0a4.tar.gz']]

    def __repr__(self):
        return "<%s for %r>" %(self.__class__.__name__, self.url)



###############################################################################
#
# setup helper
#
###############################################################################

_orgPYPIPRoxyConnectionClass = None

def setUpFakeXMLRPCPYPI(test):
    global _orgPYPIPRoxyConnectionClass
    _orgPYPIPRoxyConnectionClass = mypypi.api._connectionClass
    mypypi.api._connectionClass = FakeXMLRPCPYPI


def tearDownFakeXMLRPCPYPI(test):
    mypypi.api._connectionClass = _orgPYPIPRoxyConnectionClass

_orgUrlOpener = None

def setUpFakeUrlOpener(test):
    global _orgUrlOpener
    _orgUrlOpener = mypypi.api._urlopen
    mypypi.api._urlopen = fakeUrlOpener

def tearDownFakeUrlOpener(test):
    mypypi.api._urlopen = _orgUrlOpener

###############################################################################
#
# placeful setup/teardown
#
###############################################################################

def placefulSetUp(test):
    site = setup.placefulSetUp(site=True)
    test.globs['rootFolder'] = site
    setUpFakeXMLRPCPYPI(test)


def placefulTearDown(test):
    setup.placefulTearDown()
    tearDownFakeXMLRPCPYPI(test)


def placefulSetUpWithRealXMLRPC(test):
    site = setup.placefulSetUp(site=True)
    test.globs['rootFolder'] = site


def placefulTearDownWithRealXMLRPC(test):
    setup.placefulTearDown()

###############################################################################
#
# functional layer
#
###############################################################################

def getRootFolder():
    return functional.FunctionalTestSetup().getRootFolder()

def cleanFSFolders():
    p1 = p01.tmp.storage.getTMPStoragePath()
    shutil.rmtree(p1)
    os.mkdir(p1)
    p2 = p01.fsfile.storage.getFSStoragePath()
    shutil.rmtree(p2)
    os.mkdir(p2)

def doctestSetUp(test):
    cleanFSFolders()
    setUpFakeXMLRPCPYPI(test)
    setUpFakeUrlOpener(test)

def doctestTearDown(test):
    cleanFSFolders()
    tearDownFakeXMLRPCPYPI(test)
    tearDownFakeUrlOpener(test)

FTESTING_ZCML = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
FTESTING_ZCML = os.path.abspath(FTESTING_ZCML)

PYPIFunctionalLayer = functional.ZCMLLayer(FTESTING_ZCML, __name__, 'Functional')

def FunctionalDocFileSuite(path, **kw):
    """Including relative path setup."""
    globs = {'getRootFolder': getRootFolder}
    if 'globs' in kw:
        globs.update(kw['globs'])
        del kw['globs']

    kw['setUp'] = kw.get('setUp', doctestSetUp)
    kw['tearDown'] = kw.get('tearDown', doctestTearDown)
    kw['optionflags'] = kw.get('optionflags',
                               doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

    if 'package' not in kw:
        kw['package'] = doctest._normalize_module(kw.get('package', None))
    kw['module_relative'] = kw.get('module_relative', True)

    suite = functional.FunctionalDocFileSuite(
            path,
            globs=globs,
            **kw)

    suite.layer = PYPIFunctionalLayer
    return suite