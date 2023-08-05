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

import zope.interface
import zope.component
import zope.event
import zope.lifecycleevent
from zope.schema.fieldproperty import FieldProperty
from zope.container import btree

from z3c.configurator import configurator

from p01.tmp.interfaces import ITMPStorage
from p01.fsfile.interfaces import IFSStorage
from p01.fsfile.file import FSFile

import mypypi.api
from mypypi.i18n import MessageFactory as _
from mypypi import interfaces
from mypypi.exceptions import PackageError


class ReleaseMixin(btree.BTreeContainer):
    """Release representation."""

    published = FieldProperty(interfaces.IRelease['published'])

    author = FieldProperty(interfaces.IRelease['author'])
    authorEmail = FieldProperty(interfaces.IRelease['authorEmail'])
    cheesecakeCodeKwaliteeId = FieldProperty(
        interfaces.IRelease['cheesecakeCodeKwaliteeId'])
    cheesecakeDocumentationId = FieldProperty(
        interfaces.IRelease['cheesecakeDocumentationId'])
    cheesecakeInstallabilityId = FieldProperty(
        interfaces.IRelease['cheesecakeInstallabilityId'])
    classifiers = FieldProperty(interfaces.IRelease['classifiers'])
    description = FieldProperty(interfaces.IRelease['description'])
    downloadURL = FieldProperty(interfaces.IRelease['downloadURL'])
    homePage = FieldProperty(interfaces.IRelease['homePage'])
    keywords = FieldProperty(interfaces.IRelease['keywords'])
    license = FieldProperty(interfaces.IRelease['license'])
    maintainer = FieldProperty(interfaces.IRelease['maintainer'])
    maintainerEmail = FieldProperty(interfaces.IRelease['maintainerEmail'])
    obsoletes = FieldProperty(interfaces.IRelease['obsoletes'])
    platform = FieldProperty(interfaces.IRelease['platform'])
    protocolVersion = FieldProperty(interfaces.IRelease['protocolVersion'])
    provides = FieldProperty(interfaces.IRelease['provides'])
    pypiHidden = FieldProperty(interfaces.IRelease['pypiHidden'])
    pypiOrdering = FieldProperty(interfaces.IRelease['pypiOrdering'])
    requires = FieldProperty(interfaces.IRelease['requires'])
    stableVersion = FieldProperty(interfaces.IRelease['stableVersion'])
    summary = FieldProperty(interfaces.IRelease['summary'])

    @property
    def version(self):
        # on LocalRelease version == __name__
        return self.__name__


    def __setitem__(self, __name__, releaseFile):
        """Add a new release."""
        if not interfaces.IReleaseFile.providedBy(releaseFile):
            raise ValueError('Not a release file given.')
        super(ReleaseMixin, self).__setitem__(__name__, releaseFile)

    @property
    def isPublished(self):
        if not self.published:
            return False
        published = False
        for releaseFile in self.values():
            if releaseFile.isPublished:
                return True
        return False

    def __repr__(self):
        return "<%s %r>" %(self.__class__.__name__, self.__name__)


class LocalRelease(ReleaseMixin):
    """Local release representation."""

    zope.interface.implements(interfaces.ILocalRelease)

    def update(self, data):
        # apply values if available
        mypypi.api.applyReleaseData(self, data)


class MirrorRelease(ReleaseMixin):
    """Mirror release representation."""

    zope.interface.implements(interfaces.IMirrorRelease)

    @property
    def pypiURL(self):
        if self.__parent__ is None:
            # only happens in InterfaceBaseTest, how bad that we do not test
            # this right in verifyObject
            return u''
        return self.__parent__.pypiURL

    @property
    def url(self):
        if self.__parent__ is None:
            # only happens in InterfaceBaseTest, how bad that we do not test
            # this right in verifyObject
            return u''
        return '%s/%s/%s' % (self.pypiURL, self.__parent__.__name__,
            self.__name__)

    def update(self):
        # update relase data for this release
        pkgName = self.__parent__.__name__
        version = self.__name__
        releaseURL = '%s/%s/%s' % (self.pypiURL, pkgName, version)
        try:
            info = mypypi.api.fetchReleaseData(pkgName, version, self.pypiURL)
        except PackageError, e:
            msg = _('Error: $error, can not get release data for package: '
                    '$name and version: $version',
                        mapping={'error':str(e), 'name':self.context.__name__,
                        'version':self.__name__})
            mypypi.api.logMirrorError(msg, releaseURL)
            return None
        # apply values if available
        mypypi.api.applyReleaseData(self, info)
        msg = _('Updated release data for: $release',
            mapping={'release': self.__name__})
        mypypi.api.logMirrorHistory(msg, releaseURL)

        # update release files
        try:
            dataList = mypypi.api.fetchAllPackageReleaseURLs(pkgName, version,
                self.pypiURL)
        except PackageError, e:
            msg = _('Error: $error, can not get package release urls for package: '
                    '$name', mapping={'error': str(e),
                        'name': self.__name__})
            mypypi.api.logMirrorError(msg, releaseURL)
            return None

        for data in dataList:
            # get release data
            fileName = data['filename']
            if fileName in self.keys():
                # skip existing release files
                continue

            # force to use unicode path name
            fileName = unicode(fileName)
            url = data['url']
            md5Digest = data['md5_digest']
            try:
                fData = mypypi.api.fetchReleaseFile(url, fileName, md5Digest)
            except PackageError, e:
                continue
            # create FSFile
            tmpStorage = zope.component.queryUtility(ITMPStorage)
            tmpFile = tmpStorage.getTMPFile()
            tmpFile.write(fData)
            tmpFile.close()

            # create MirrorRelease
            fsStorage = zope.component.getUtility(IFSStorage)
            # store file in mirror storage
            obj = fsStorage.store(tmpFile, fileName, fsNameSpace=u'mirror')
            mypypi.api.applyReleaseFileData(obj, data)

            self[unicode(fileName)] = obj
            msg = _('Added release file: $fileName',
                mapping={'fileName': fileName})
            mypypi.api.logMirrorHistory(msg, url)
            configurator.configure(obj, None)

        # marke as modified which will force to save a new modified date
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(self))


class ReleaseFile(FSFile):
    """Release file system file."""

    zope.interface.implements(interfaces.IReleaseFile)

    commentText = FieldProperty(interfaces.IReleaseFile['commentText'])
    downloads = FieldProperty(interfaces.IReleaseFile['downloads'])
    hasSig = FieldProperty(interfaces.IReleaseFile['hasSig'])
    md5Digest = FieldProperty(interfaces.IReleaseFile['md5Digest'])
    packageType = FieldProperty(interfaces.IReleaseFile['packageType'])
    pythonVersion = FieldProperty(interfaces.IReleaseFile['pythonVersion'])
    url = FieldProperty(interfaces.IReleaseFile['url'])

    published = FieldProperty(interfaces.IReleaseFile['published'])

    @property
    def isPublished(self):
        return self.published

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)


class LocalReleaseConfigurator(configurator.ConfigurationPluginBase):
    """Configure the ILocalRelease."""

    zope.component.adapts(interfaces.ILocalRelease)

    def __call__(self, data):
        """This get called by SubmitPage and LocalReleaseAddForm."""
        self.context.update(data)


class MirrorReleaseConfigurator(configurator.ConfigurationPluginBase):
    """Configure the IMirrorRelease."""

    zope.component.adapts(interfaces.IMirrorRelease)

    def __call__(self, data):
        self.context.update()
