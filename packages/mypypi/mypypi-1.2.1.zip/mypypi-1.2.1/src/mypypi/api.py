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

import StringIO
import cStringIO
import os
import re
import sys
import types
import urllib
import urllib2
import urlparse
import xmlrpclib
import zipfile
import HTMLParser
from glob import fnmatch
from pkg_resources import parse_version
from docutils.core import publish_parts
try:  
   from hashlib import md5 
except ImportError: 
   from md5 import md5

from BeautifulSoup import BeautifulSoup

from zope.security import checkPermission

from z3c.indexer import indexer

from mypypi import interfaces
from mypypi import logger
from mypypi import versionpredicate
from mypypi.exceptions import PackageError


# logging
def logLocalHistory(message):
    log = logger.getLocalLogger()
    log.logHistory(message)

def logLocalError(message):
    log = logger.getLocalLogger()
    log.logError(message)

def logMirrorHistory(message, path=None):
    log = logger.getMirrorLogger()
    log.logHistory(message, path)

def logMirrorError(message, path=None):
    log = logger.getMirrorLogger()
    log.logError(message, path)


# simple page rendering
PAGE = """<html>
<head><title>%s</title>
</head>
<body>
<h1>%s</h1>
%s
</body>
</html>
"""

def renderOneLineLink(url, content):
    return '<a href="%s">%s</a>' % (url, content)

def renderPage(page):
    return PAGE % (page.title, page.title, page.body)



def markItemsAsPublished(item, state=True):
    item.published = state
    indexer.index(item)
    if interfaces.IPackage.providedBy(item) or \
        interfaces.ILocalRelease.providedBy(item) or \
        interfaces.IMirrorRelease.providedBy(item):
        for child in item.values():
            markItemsAsPublished(child, state)
            indexer.index(child)


def checkViewPermission(obj):
    return checkPermission('mypypi.View', obj)


def checkManagePackagesPermission(obj):
    return checkPermission('mypypi.ManagePackages', obj)


def checkViewable(obj=None):
    if obj is None:
        return False
    # check first permision then publish stati, otherwise we will
    #  run into Unauthorized if we access isPublished first
    return checkPermission('mypypi.View', obj) and  obj.isPublished

# Pypi related API
# exposed for testing
_connectionClass = xmlrpclib.Server

def getPYPIProxy(url=None):
    """Returns a pypi XML-RPC connection."""
    if url is None:
        url = 'http://pypi.python.org/pypi'
    return _connectionClass(url)


def fetchPackageList(url='http://pypi.python.org/pypi', filter=None):
    pypiProxy = getPYPIProxy(url)
    pkgNames = pypiProxy.list_packages()
    if filter is None:
        return pkgNames

    filteredNames = []
    for name in pkgNames:
        if not True in [fnmatch.fnmatch(name, f) for f in filter]:
            continue
        filteredNames.append(name)
    return filteredNames


def fetchReleaseData(packageName, version, url='http://pypi.python.org/pypi'):
    """Fetch release data

    This method returns the same output as the pypi RPC method called
    release_data returns.
    """
    pypiProxy = getPYPIProxy(url)
    return pypiProxy.release_data(packageName, version)


def fetchPackageReleases(packageName, show_hidden=True,
    url='http://pypi.python.org/pypi'):
    """Fetch package release (version) names.

    This method returns the same output as the pypi RPC method called
    package_releases returns.
    """
    pypiProxy = getPYPIProxy(url)
    rv = pypiProxy.package_releases(packageName, show_hidden)
    if not rv and '-' in packageName:
        packageName = packageName.replace('-', '_')
        rv = pypiProxy.package_releases(packageName, show_hidden)
    return packageName, rv


def fetchPackageReleaseURLs(packageName, version,
    pypiURL='http://pypi.python.org/pypi'):
    """Fetch package releases urls and data.

    This method returns the same output as the pypi RPC method called
    release_urls returns.
    """
    pypiProxy = getPYPIProxy(pypiURL)
    return pypiProxy.release_urls(packageName, version)


# TODO: this method get called for every release version, see the method
# update in release.py line: 128
# We should probably optimize the concept and cache the fetched links
# in a session. This whold prevent to call the same page more then once
# for fetch external links.
def fetchAllPackageReleaseURLs(pkgName, version,
    pypiURL='http://pypi.python.org/pypi'):
    """Fetch package releases urls.

    This method collects package release file urls via RPC or external
    urls from the simple index or from the package page. The method collects
    the in the described order. We skip future link collection if we found urls
    from the RPC method. And we only collect urls from the simple index or the
    pcakge release page if we do not get links from the RPC method.

    This return only a list of dicts containing url, filename and an optional
    hash.

    """
    res = []
    localURLs = fetchPackageReleaseURLs(pkgName, version, pypiURL)
    for data in localURLs:
        res.append({'url': data['url'],
                    'filename': data['filename'],
                    'md5_digest': data['md5_digest']})
    if res:
        # if we found release urls we do not collect external links.
        return res
    # if we didn't find urls, check the simple index page

# TODO: we implicit guess the simple index url, this should go to a site
# attribute. Also check if we shoudl provide a per package index setup. This
# whould allow mirror packages from different servers. Right now we only allow
# to mirror packages from one server, by default http://pypi.python.org/pypi
    pypiBase = pypiURL[:-5]
    simpleURL = '%s/simple/%s' % (pypiBase, pkgName)
    simpleURLs = list(getLinks(simpleURL, version))
    for sURL, fName, h in simpleURLs:
        res.append({'url': sURL,
                    'filename': fName,
                    'md5_digest': h})
    # TODO: check the following concept. It works now for any package which
    # follows the pypi guidline including external url as long as it is not
    # so messed up like the PIL package.
    # I think there could be a better way to fetch download urls.
    # Check the following pages for find out if we can find a better way to
    # fetch release files for a give package version:
    # http://pypi.python.org/simple/pyPdf
    # http://pypi.python.org/simple/PIL
    # http://pypi.python.org/simple/z3c.form
    pkgURL = '%s/%s/%s' % (pypiURL, pkgName, version)
    indexPage = fetchPage(pkgURL)

    # TODO: if we change this make it optional or at least fetch external links
    # only if we found externlas links the first time. Prevent fetching external
    # links if we didn't found the first time during update.
    externalURLs = list(fetchExternalLinks(pkgName, version, indexPage))
    for eURL in externalURLs:
        res.append({'url': eURL,
                    'filename': urlparse.urlsplit(eURL)[2].split('/')[-1],
                    'md5_digest': None})
    return res


def checkFileName(url, version):
    """Check for valid filename and version.

    Right now we allow the following file/version formats.

    - <package name>1.1.<file ending>
    - <package name>1.1-<file ending>
    - <package name>1.1a-<file ending>
    - <package name>1.1dev-<file ending>

    This will prevent that we fetch a package with the wrong package name
    and with a wrong version. This also includes to prevent fetching
    a version 1.12 for a 1.1 release.

    The used pattern looks like: *%s[a-z-.]*

    """
    v = '*%s[a-z-.]*' % version
    for ending in ['*.zip', '*.tgz', '*.egg', '*.tar.gz', '*.tar.bz2']:
        if fnmatch.fnmatch(url, ending) and fnmatch.fnmatch(url, v):
            return True
    return False


def fetchPage(url):
    """Fetch html from package page by given url."""
    try:
        html = urllib2.urlopen(url).read()
    except urllib2.HTTPError, v:
        if '404' in str(v):
            raise PackageError(
                "Package not available (404): %s" % url)
        else:
            raise PackageError(
                "Package not available (unknown reason): %s" % \
                    url)
    except urllib2.URLError, v:
        raise PackageError("URL Error: %s " % \
            url)
    except Exception, e:
        raise PackageError('Generic error: %s' % e)
    return html


def fetchLinks(html):
    """Fetch links from given html content."""
    links = []
    try:
        soup = BeautifulSoup(html)
        append = links.append
        for link in soup.findAll("a"):
            href = link.get("href")
            if href:
                append(href)
    except HTMLParser.HTMLParseError, e:
        pass
    return links


# TODO: probably we can find a better concept for this
def fetchExternalLinks(pkgName, version, html, follow_external_index_pages=True):
    """ pypi has external "download_url"s. We try to get anything
        from there too. This is really ugly and I'm not sure if there's
        a sane way.  The download_url directs either to a website which
        contains many download links or directly to a package.
    """
    links = fetchLinks(html)
    for link in links:
        # check if the link points directly to a file and if the file matches
        # return the link
        if checkFileName(link, version):
            yield link
            continue

        # fetch what is behind the link and see if it's html.
        # If it is html, download anything from there.
        # This is extremely unreliable and therefore commented out.

        if follow_external_index_pages:
            try:
                site = urllib2.urlopen(link)
            except Exception, e:
                continue

            if site.headers.type != "text/html":
                continue

            # we have a valid html page now. Parse links and download them.
            # They have mostly no md5 hash.
            html = site.read()
            real_download_links = fetchLinks(html)
            candidates = list()
            for real_download_link in real_download_links:
                # build absolute links

                real_download_link = urllib.basejoin(
                    site.url, real_download_link)
                if checkFileName(real_download_link, version):

                    # we're not interested in dev packages
                    dev_package_regex = re.compile(r'\ddev[-_]')
                    if not dev_package_regex.search(real_download_link):

                        # Consider only download links that starts with
                        # the current package name
                        filename = urlparse.urlsplit(
                            real_download_link)[2].split('/')[-1]
                        if not filename.startswith(pkgName):
                            continue

                        candidates.append(real_download_link)

            def sort_candidates(url1, url2):
                """ Sort all download links by package version """
                parts1 = urlparse.urlsplit(url1)[2].split('/')[-1]
                parts2 = urlparse.urlsplit(url2)[2].split('/')[-1]
                return cmp(parse_version(parts1), parse_version(parts2))

            # and return the 20 latest files
            candidates.sort(sort_candidates)
            for c in candidates[-20:][::-1]:
                yield c


def getLinks(url, version):
    """Return an iterator with links."""
    page = fetchPage(url)
    for link in fetchLinks(page):
        # then handle "normal" packages in pypi.
        (url, hash) = urllib.splittag(link)
        if not hash:
            continue
        try:
            (hashname, hash) = hash.split("=")
        except ValueError:
            continue
        if not hashname == "md5":
            continue

        if not checkFileName(url, version):
            continue

        yield (url, os.path.basename(url), hash)

#put this here for testing hook
_urlopen = urllib2.urlopen

def fetchReleaseFile(url, filename, md5Digest=None):
    """Fetches a release file and checks for the md5Digest if given."""
    try:
        data = _urlopen(url).read()
    except urllib2.HTTPError, v:
        if '404' in str(v):             # sigh
            raise PackageError("404: %s" % url)
        raise PackageError(
            "Couldn't download (HTTP Error): %s" % url)
    except urllib2.URLError, v:
        raise PackageError("URL Error: %s " % url)
    except:
        raise PackageError(
            "Couldn't download (unknown reason): %s" % url)
    if md5Digest:
        # check for md5 checksum
        data_md5 = md5(data).hexdigest()
        if md5Digest != data_md5:
            raise PackageError(
                "MD5 sum does not match: %s / %s for release file %s" % (
                    md5Digest, data_md5, url))
    return data


# distutil upload helper
allowedFileNames = re.compile(r'.+?\.(exe|tar\.gz|bz2|egg|rpm|deb|zip|tgz)$',
    re.I)

def makeList(value):
    # convert to unicode lists
    return [unicode(v) for v in value]

# format is: {incoming_field: (camelcasedField, valueConverter)}
RELEASE_DATA = {
    '_pypi_hidden': ('pypiHidden', int),
    '_pypi_ordering': ('pypiOrdering', int),
    'author': ('author', unicode),
    'author_email': ('authorEmail', unicode),
    'cheesecake_code_kwalitee_id': ('cheesecakeCodeKwaliteeId', int),
    'cheesecake_documentation_id': ('cheesecakeDocumentationId', int),
    'cheesecake_installability_id': ('cheesecakeInstallabilityId', int),
    'classifiers': ('classifiers', makeList),
    'description': ('description', unicode),
    'download_url': ('downloadURL', unicode),
    'home_page': ('homePage', unicode),
    'keywords': ('keywords', unicode),
    'license': ('license', unicode),
    'maintainer': ('maintainer', unicode),
    'maintainer_email': ('maintainerEmail', unicode),
    'md5_digest': ('md5Digest', str),
    'name': ('name', unicode),
    'obsoletes': ('obsoletes', makeList),
    'platform': ('platform', unicode),
    'protocol_version': ('protocolVersion', unicode),
    'provides': ('provides', makeList),
    'requires': ('requires', makeList),
    'stable_version': ('stableVersion', unicode),
    'summary': ('summary', unicode),
}

RELEASE_FILE_DATA = {
    'comment_text': ('commentText', unicode),
    'downloads': ('downloads', int),
    # distutils uses filetype and pypi uses packagetype, we use packageType
    'filetype': ('packageType', unicode),
    'has_sig': ('hasSig', bool),
    'md5_digest': ('md5Digest', str),
    # distutils uses filetype and pypi uses packagetype, we use packageType
    'packagetype': ('packageType', unicode),
    'python_version': ('pythonVersion', unicode),
    'size': ('size', int),
    'url': ('url', str),
}

def applyData(context, data, lookupTable):
    for key, value in data.items():
        # oh my, we only use camel case
        # release data
        newData = lookupTable.get(key)
        if newData is None:
            # skip unknown attributes
            continue

        key = newData[0] # camel case key
        converter = newData[1] # converter

        # convert value
        if converter is not None and value:
            try:
                value = converter(value)
            except ValueError, e:
                raise ValueError("Can't convert value %s to %s for %s" % (
                    value, converter, key))
        # apply value
        if value:
            setattr(context, key, value)


def applyReleaseData(context, data):
    applyData(context, data, RELEASE_DATA)

def applyReleaseFileData(context, data):
    applyData(context, data, RELEASE_FILE_DATA)


def verifyMetaData(data, verifyClassifiers=True):
    """ Validate the contents of the metadata.
    """
    if not data.get('name', ''):
        raise ValueError, 'Missing required field "name"'
    if not data.get('version', ''):
        raise ValueError, 'Missing required field "version"'
    if data.has_key('metadata_version'):
        del data['metadata_version']

    # make sure relationships are lists
    for name in ('requires', 'provides', 'obsoletes'):
        if data.has_key(name) and not isinstance(data[name], list):
            data[name] = [data[name]]

    # make sure classifiers is a list
    if data.has_key('classifiers'):
        classifiers = data['classifiers']
        if not isinstance(classifiers, list):
            classifiers = [classifiers]
        data['classifiers'] = classifiers

    # check requires and obsoletes
    def validate_version_predicates(col, sequence):
        try:
            map(versionpredicate.VersionPredicate, sequence)
        except ValueError, message:
            raise ValueError, 'Bad "%s" syntax: %s'%(col, message)
    for col in ('requires', 'obsoletes'):
        if data.has_key(col) and data[col]:
            validate_version_predicates(col, data[col])

    # check provides
    if data.has_key('provides') and data['provides']:
        try:
            map(versionpredicate.check_provision, data['provides'])
        except ValueError, message:
            raise ValueError, 'Bad "provides" syntax: %s'%message

    # check classifiers depending on verifyClassifiers which depends on site
    # settings for checkClassifiersOnVerify and checkClassifiersOnUpload
    if data.has_key('classifiers'):
        d = {}
        for cKey in getClassifierKeys():
            d[cKey] = 1
        cf = {}
        classifiers = data['classifiers']
        if not isinstance(classifiers, types.ListType):
            # huh, only one classifier given
            classifiers = [classifiers]
        for entry in classifiers:
            if d.has_key(entry):
                # only use existent classifiers
                cf[entry] = 1
            elif verifyClassifiers:
                # raise error if defined in site
                raise ValueError, 'Invalid classifier "%s"'%entry
        data['classifiers'] = cf.keys()


def isDistutilsFile(content, filename, filetype):
    """Ensure that we have a valid distutils file."""
    if filename.endswith('.exe'):
        # check for valid exe
        if filetype != 'bdist_wininst':
            return False
        try:
            t = StringIO.StringIO(content)
            t.filename = filename
            z = zipfile.ZipFile(t)
            l = z.namelist()
        except zipfile.error:
            return False
        for zipname in l:
            if not safe_zipnames.match(zipname):
                return False
    elif filename.endswith('.zip'):
        # check for valid zip
        try:
            t = StringIO.StringIO(content)
            t.filename = filename
            z = zipfile.ZipFile(t)
            l = z.namelist()
        except zipfile.error:
            return False
        for entry in l:
            parts = os.path.split(entry)
            if len(parts) == 2 and parts[1] == 'PKG-INFO':
                # eg. "roundup-0.8.2/PKG-INFO"
                break
        else:
            return False
    return True


# cache this
classifiersDataPath = os.path.join(os.path.dirname(__file__),
    'classifiers.data')

pypiClassifiersURL = 'http://pypi.python.org/pypi?%3Aaction=list_classifiers'

class ClassifierBuilder(object):
    """ClassifierBuilder."""

    def __init__(self, pypiClassifiersURL=pypiClassifiersURL):
        fData = open(classifiersDataPath)

#        # avoid calling data from pypi
#        import socket
#        try:
#            old_timeout = socket.getdefaulttimeout()
#            socket.setdefaulttimeout(10)
#            try:
#                fData = urllib2.urlopen(pypiClassifiersURL)
#            finally:
#                socket.setdefaulttimeout(old_timeout)
#        except urllib2.URLError:
#            # use the default data if we have no access to pypi
#            fData = open(classifiersDataPath)

        try:
            self._lines = sorted([line.strip() for line in
                                  fData.readlines()])
        finally:
            fData.close()

        # setup data dict
        ids = {}
        for line in self._lines:
            split = line.split(' :: ')
            i = -1
            id_, title = self._getIdAndTitle(split[i])
            while id_ in ids:
                i -= 1
                id_ = '%s %s' % (split[i], id_)
                id_, title = self._getIdAndTitle(id_)
            ids[line] = id_, title
        self.data = ids

    def _getIdAndTitle(self, field):
        """Returns id and title."""
        return field.lower().replace(' ', ''), field

    def get(self):
        """Returns data."""
        return self.data

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()

    def list(self):
        return self._lines


def getClassifierData():
    # cache this in ram cache for a period given from IPYPISite
    return ClassifierBuilder()

def getClassifierKeys():
    # cache this in ram cache for a period given from IPYPISite
    builder = ClassifierBuilder()
    return builder.keys()

def listClassifiers():
    builder = ClassifierBuilder()
    return builder.list()

# moved from docutils, this is gone in newer docutils
def trim_docstring(text):
    """
    Trim indentation and blank lines from docstring text & return it.

    See PEP 257.
    """
    if not text:
        return text
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = text.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxint:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)

def formatDescription(source):
    """Pypi description formatter."""
    # trim source
    source = trim_docstring(source)

    settings_overrides={
        'raw_enabled': '0',  # no raw HTML code
        'file_insertion_enabled': '0',  # no file/URL access
        'halt_level': 2,  # at warnings or errors, raise an exception
        'report_level': 5,  # never report problems with the reST code
        }

    # capture publishing errors, they go to stderr
    old_stderr = sys.stderr
    sys.stderr = s = cStringIO.StringIO()
    parts = None
    try:
        # convert reStructuredText to HTML
        parts = publish_parts(source=source, writer_name='html',
                              settings_overrides=settings_overrides)
    except:
        pass

    sys.stderr = old_stderr

    # original text if publishing errors occur
    if parts is None or len(s.getvalue()) > 0:
        output = "".join('<PRE>\n' + source + '</PRE>')
    else:
        output = parts['body']

    return output
