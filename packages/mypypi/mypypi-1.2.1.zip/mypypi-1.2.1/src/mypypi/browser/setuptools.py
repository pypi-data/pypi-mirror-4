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
import transaction
import zope.event
import zope.lifecycleevent
from zope.publisher.browser import BrowserPage
from zope.component import hooks

from z3c.configurator import configurator

from p01.tmp.interfaces import ITMPStorage
from p01.fsfile.interfaces import IFSStorage

import mypypi.api
from mypypi.i18n import MessageFactory as _
from mypypi import package
from mypypi import release
from mypypi import versionpredicate


def errorResponse(request, msg, status=400):
    if request is None:
        raise ValueError, msg
    # doom the transaction
    transaction.doom()
    response = request.response
    response.setStatus(status, reason=msg)
    if status == 401:
        response.setHeader('WWW-Authenticate', 'basic realm="pypi"', 1)
    return msg


def getPackageAndRelease(name, version, data, msgs):
    site = hooks.getSite()
    pkg = site.get(name)
    if pkg is None:
        pkg = package.LocalPackage()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(pkg))
        site[name] = pkg
        configurator.configure(pkg, None)
        msgs.append('Created Package: %s' % name)
    rel = pkg.get(version)
    if rel is None:
        rel = release.LocalRelease()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(rel))
        pkg[version] = rel
        configurator.configure(rel, data)
        msgs.append('Created Release: %s' % version)
    else:
        rel.update(data)
        msgs.append('Updated Release: %s' % version)
    return pkg, rel


class ListClassifiersPage(BrowserPage):
    """``list_classifiers`` page used by distutil command
    ``setup.py register --list-classifiers``.
    """
    def __call__(self):
        """List classifiers."""
        return '\n'.join(mypypi.api.listClassifiers())


class VerifyPage(BrowserPage):
    """``verify`` page used by distutil command ``setup.py register --dry-run``.
    """

    def __call__(self):
        """Verify package metadata."""
        data = self.request.form
        site = hooks.getSite()
        verifyClassifiers = site.checkClassifiersOnVerify
        try:
            mypypi.api.verifyMetaData(data, verifyClassifiers)
        except ValueError, e:
            err = '%s' % e
            return errorResponse(self.request, err)

        return 'OK'


class SubmitPage(BrowserPage):
    """``submit`` page used by distutil command ``setup.py register``."""

    def __call__(self):
        """Receive package data and create package and release.

        The given form data is a dict which contains the following content:

        {u'': u'submit',
         u'license': u'ZPL 2.1',
         u'name': u'z3c.schema',
         u'metadata_version': u'1.0',
         u'author': u'Zope Community',
         u'home_page': u'http://pypi.python.org/pypi/z3c.schema',
         u'download_url': u'UNKNOWN',
         u'summary': u'Additional schema fields for Zope 3',
         u'author_email': u'zope3-dev@zope.org',
         u'version': u'0.5.0',
         u'platform': u'UNKNOWN',
         u'keywords': u'zope zope3 z3c schema',
         u'classifiers': [u'Development Status :: 4 - Beta',
                          u'Environment :: Web Environment',
                          u'Intended Audience :: Developers',
                          u'License :: OSI Approved :: Zope Public License',
                          u'Programming Language :: Python',
                          u'Natural Language :: English',
                          u'Operating System :: Microsoft :: Windows',
                          u'Topic :: Internet :: WWW/HTTP',
                          u'Framework :: Zope3'],
         u'description': u'This package provides ... Initial release\n'}

        """
        data = self.request.form
        site = hooks.getSite()
        verifyClassifiers = site.checkClassifiersOnUpload
        try:
            mypypi.api.verifyMetaData(data, verifyClassifiers)
        except ValueError, message:
            err = 'Validation error: %s' % message
            return errorResponse(self.request, err)

        name = data['name']
        version = data['version']

        # make sure the _pypi_hidden flag is set if not given
        if not data.has_key('_pypi_hidden'):
            data['_pypi_hidden'] = False

        # get or create the package
        msgs = []
        pkg, rel = getPackageAndRelease(name, version, data, msgs)

# TODO: implement download_url concept
        # create download link if a ``download_url`` is given

        return '\n'.join(msgs)


class FileUploadPage(BrowserPage):
    """``file_upload`` page used by distutil command ``setup.py upload``."""

    def __call__(self):
        """Receive release package upload.

        The given form data is a dict which contains the following content:

        {u'comment': u'',
         u'': u'file_upload',
         u'protocol_version': u'1',
         u'md5_digest': u'7a2b1ff51513aaa365a90e0864f2ccdf',
         u'filetype': u'sdist',
         u'pyversion': u'',
         u'content': <zope.publisher.browser.FileUpload object at 0x02944BF0>,
         u'version': u'0.5.0dev',
         u'name': u'z3c.schema'}

        """
        data = self.request.form

        # figure the package name and version
        name = data.get('name')
        if name is None:
            msg = "'name' is required but missing"
            return errorResponse(self.request, msg)
        version = data.get('version')
        if version is None:
            msg = "'version' is required but missing"
            return errorResponse(self.request, msg)

        # check name
        msgs = []
        pkg, rel = getPackageAndRelease(name, version, data, msgs)

        content = data.get('content')
        if content is None:
            msg = 'Content is required but missing'
            return errorResponse(self.request, msg)
        filetype = data.get('filetype')
        if filetype is None:
            msg = 'Filetype is required but missing'
            return errorResponse(self.request, msg)

        # check for valid filenames
        fileName = content.filename
        if not mypypi.api.allowedFileNames.match(fileName):
            msg = 'Invalid file given: %s' % fileName
            return errorResponse(self.request, msg)

        # check for path in filenames
        if '/' in fileName or '\\' in fileName:
            msg = 'Invalid file given: %s' % fileName
            return errorResponse(self.request, msg)

        # get content
        content.close()
        content = content.read()
        tmpStorage = zope.component.getUtility(ITMPStorage)
        tmpFile = tmpStorage.getTMPFile()
        tmpFile.write(content)
        tmpFile.close()

# TODO: the zip file check doesn't pass?
#        # check for valid contents based on the type
#        if not mypypi.api.isDistutilsFile(content, fileName, filetype):
#            msg = 'Not a distutils file give: %s (%s)' % (
#                fileName, filetype)
#            return errorResponse(self.request, msg)

        # digest content
        md5Digest = data.get('md5_digest')
        if md5Digest:
            m = md5.new()
            m.update(content)
            if md5Digest != m.hexdigest():
                msg = 'MD5 digest does not match with the uploaded file'
                return errorResponse(self.request, msg)

        # add history entry
        msg = _('Uploaded release file: $fileName with distutil',
            mapping={'fileName': fileName})
        mypypi.api.logLocalHistory(msg)

        # create release file
        fsStorage = zope.component.getUtility(IFSStorage)
        # store in distutils storage
        relFile = fsStorage.store(tmpFile, fileName, fsNameSpace=u'distutils')
        mypypi.api.applyReleaseFileData(relFile, data)
        if not relFile.size:
            relFile.size = len(content)

        # remove existing release file and set history entry
        if rel.get(fileName, None) is not None:
            del rel[fileName]
            msgs.append('Updated Release File: %s' % fileName)
        else:
            msgs.append('Created Release File: %s' % fileName)

        # add and configure file
        rel[unicode(fileName)] = relFile

        return '\n'.join(msgs)
