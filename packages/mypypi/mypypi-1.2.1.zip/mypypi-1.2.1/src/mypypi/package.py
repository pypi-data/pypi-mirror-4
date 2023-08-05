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

import xmlrpclib

import zope.interface
import zope.component
import zope.event
import zope.lifecycleevent
from zope.schema.fieldproperty import FieldProperty
from zope.container import btree

from z3c.configurator import configurator

import mypypi.api
from mypypi.i18n import MessageFactory as _
from mypypi import interfaces
from mypypi import release
from mypypi.exceptions import PackageError
from mypypi.exceptions import MissingReleases


class PackageMixin(btree.BTreeContainer):
    """IPackage mixin."""

    published = FieldProperty(interfaces.IPackage['published'])

    def __setitem__(self, __name__, release):
        """Disabeld, use add method instead."""
        if not interfaces.IRelease.providedBy(release):
            raise ValueError('Not a release given.')
        super(PackageMixin, self).__setitem__(__name__, release)

    @property
    def isPublished(self):
        if not self.published:
            return False
        published = False
        for release in self.values():
            if release.isPublished:
                return True
        return False

    @property
    def latest(self):
        version = ''
        current = None
        for release in self.values():
            # version is a number with letters in unicode which means
            # '0.5.0a' is later then '0.5.0'. But anyway you never should
            # use letters in release numbers. probably we should be smart and
            # support such addon letters which mark earlier releases.
            if release.version > version:
                version = release.version
                current = release
        return current

    def __repr__(self):
        return "<%s %r>" %(self.__class__.__name__, self.__name__)


class LocalPackage(PackageMixin):
    """Package located only at this server."""

    zope.interface.implements(interfaces.ILocalPackage)


class MirrorPackage(PackageMixin):
    """Package mirrored from another package index."""

    zope.interface.implements(interfaces.IMirrorPackage)

    # exposed for testing purpose
    _connectionClass = xmlrpclib.Server

    pypiURL = FieldProperty(interfaces.IMirrorPackage['pypiURL'])

    def __init__(self, pypiURL):
        super(MirrorPackage, self).__init__()
        self.pypiURL = pypiURL

    def _getConnection(self):
        return self._connectionClass(self.pypiURL, allow_none=True)

    def getName(self, name):
        fetchReleasesError = False
        try:
            name, names = mypypi.api.fetchPackageReleases(
                name, self.pypiURL)
        except PackageError, e:
            fetchReleasesError = True
        if not names or fetchReleasesError:
            msg = _('Error: Can not get package releases for package: '
                    '$name', mapping={'name': self.__name__})
            mypypi.api.logMirrorError(msg, self.pypiURL)
            raise MissingReleases(self.__name__)
        return name

    @property
    def url(self):
        return '%s/%s' % (self.pypiURL, self.__name__)

    def update(self):
        keyNames = self.keys()
        fetchReleasesError = False
        try:
            unused, names = mypypi.api.fetchPackageReleases(
                self.__name__, self.pypiURL)
        except PackageError, e:
            fetchReleasesError = True
        if not names or fetchReleasesError:
            msg = _('Error: Can not get package releases for package: '
                    '$name', mapping={'name': self.__name__})
            mypypi.api.logMirrorError(msg, self.pypiURL)
            raise MissingReleases(self.__name__)

        for name in names:
            # create release
            mRelease = self.get(name)
            if mRelease is not None:
                mRelease.update()
                continue
            added = True
            obj = release.MirrorRelease()
            zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
            # add release
            self[name] = obj
            # configure release which forces to fetch release files
            configurator.configure(obj, None)

        # marke as modified which will force to save a new modified date
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(self))


class MirrorPackageConfigurator(configurator.ConfigurationPluginBase):
    """Configure the IMirrorPackage."""

    zope.component.adapts(interfaces.IMirrorPackage)

    def __call__(self, data):
        self.context.update()
