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

import time

import zope.component
import zope.interface
import zope.event
import zope.lifecycleevent
from zope.schema.fieldproperty import FieldProperty
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from zope import intid
from zope.site import site
from zope.component import hooks
from zope.container import btree
from zope.authentication.interfaces import IAuthentication
from zope.authentication.interfaces import IEveryoneGroup

from z3c.authenticator.authentication import Authenticator
from z3c.authenticator.credential import HTTPBasicAuthCredentialsPlugin
from z3c.authenticator.group import GroupContainer
from z3c.authenticator.user import UserContainer
from z3c.authenticator.principalregistry import PrincipalRegistryAuthenticatorPlugin
from z3c.configurator import configurator
from z3c.indexer.interfaces import IIndex
from z3c.indexer.index import TextIndex
from z3c.indexer.index import ValueIndex

from p01.remote import processor
from p01.fsfile.interfaces import IFSStorage
from p01.fsfile.storage import FlatPathFSStorage
from p01.fsfile.storage import getFSStoragePath

import mypypi.api
from mypypi.i18n import MessageFactory as _
from mypypi import interfaces
from mypypi import authentication
from mypypi import job
from mypypi import release

START_TIME = time.time()


class PYPISite(btree.BTreeContainer, site.SiteManagerContainer,
    processor.RemoteProcessor):
    """PYPISite site."""

    zope.interface.implements(interfaces.IPYPISite)

    title = FieldProperty(interfaces.IPYPISite['title'])

    checkClassifiersOnUpload = FieldProperty(
        interfaces.IPYPISite['checkClassifiersOnUpload'])
    checkClassifiersOnVerify = FieldProperty(
        interfaces.IPYPISite['checkClassifiersOnVerify'])

    packageSynchronizerInterval = FieldProperty(
        interfaces.IPYPISite['packageSynchronizerInterval'])

    # IRemoteQueue
    autoStartMirrorScheduler = FieldProperty(
        interfaces.IPYPISite['autoStartMirrorScheduler'])

    def __init__(self):
        super(PYPISite, self).__init__()
        processor.RemoteProcessor.__init__(self)
        self.title = u'PYPISite'
        self.pypiURL = 'http://pypi.python.org/pypi'

    def __setitem__(self, __name__, package):
        """Add a new package."""
        if not interfaces.IPackage.providedBy(package):
            raise ValueError('Not a package given.')
        super(PYPISite, self).__setitem__(__name__, package)

    def syncMirrorPackages(self):
        msg = _(u'Sync Mirror Packages started')
        mypypi.api.logMirrorHistory(msg)
        for pkg in self.values():
            if interfaces.IMirrorPackage.providedBy(pkg):
                pkg.update()

    def getStartTime(self):
        return START_TIME

    # PYPI API (used in XML-RPC)
    # The pypi API allows to lookup everything from the site root
    # NOTE: this API only returns accessible items which are published
    # and the user has permission to access
    def getPackages(self):
        """Returns a list of accessible packages"""
        for pkg in self.values():
            if mypypi.api.checkViewable(pkg):
                yield pkg

    def getReleases(self, pkgName, showHidden=False):
        """Returns a list of accessible releases"""
        pkg = self.get(pkgName)
        if mypypi.api.checkViewable(pkg):
            if showHidden:
                return [rel for rel in pkg.values()
                        if mypypi.api.checkViewable(rel)]
            else:
                return [rel for rel in pkg.values()
                        if mypypi.api.checkViewable(rel) and not rel.pypiHidden]
        return []

    def getRelease(self, pkgName, version):
        pkg = self.get(pkgName)
        if pkg is not None:
            return pkg.get(version)

    def getReleaseFiles(self, pkgName, version):
        """Returns a list of accessible release files"""
        pkg = self.get(pkgName)
        if pkg is not None:
            rel = pkg.get(version)
            if rel is not None:
                return [f for f in rel.values()
                        if mypypi.api.checkViewable(f)]
        return []

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)


class PYPISiteConfigurator(configurator.ConfigurationPluginBase):
    """Configure the PYPISite site."""
    zope.component.adapts(interfaces.IPYPISite)

    def __call__(self, data):
        # setup site manager
        sm = site.LocalSiteManager(self.context)
        self.context.setSiteManager(sm)

        # Create an intid utility
        ids = intid.IntIds()
        sm['default']['IntIds' ] = ids
        sm.registerUtility(ids, intid.interfaces.IIntIds)

        # create IPackage index
        fullText = TextIndex()
        sm['default']['package.packageText'] = fullText
        sm.registerUtility(fullText, IIndex, name='package.packageText')

        valueIndex = ValueIndex()
        sm['default']['package.isPublished'] = valueIndex
        sm.registerUtility(valueIndex, IIndex, name='package.isPublished')

        fullText = TextIndex()
        sm['default']['package.releaseText'] = fullText
        sm.registerUtility(fullText, IIndex, name='package.releaseText')

        fullText = TextIndex()
        sm['default']['package.releaseClassifiers'] = fullText
        sm.registerUtility(fullText, IIndex, name='package.releaseClassifiers')

        # create IRelease index
        fullText = TextIndex()
        sm['default']['release.fullText'] = fullText
        sm.registerUtility(fullText, IIndex, name='release.fullText')

        # create IPYPIUser index
        fullText = TextIndex()
        sm['default']['user.fullText'] = fullText
        sm.registerUtility(fullText, IIndex, name='user.fullText')

        # create IHistoryEntry index
        fullText = TextIndex()
        sm['default']['historyEntry.fullText'] = fullText
        sm.registerUtility(fullText, IIndex, name='historyEntry.fullText')

        # create IErrorEntry index
        fullText = TextIndex()
        sm['default']['errorEntry.fullText'] = fullText
        sm.registerUtility(fullText, IIndex, name='errorEntry.fullText')

        # Add the pluggable authentication utility
        auth = Authenticator()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(auth))
        sm['default']['Authenticator'] = auth
        sm.registerUtility(auth, IAuthentication)

        prm = IPrincipalRoleManager(self.context)

        # setup 'groups' group container
        groups = GroupContainer(u'groups.')
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(groups))
        auth[u'groups'] = groups
        auth.authenticatorPlugins += (u'groups',)

        # setup 'Administrators' group
        grp =  authentication.PYPIGroup(u'Administrators',
            u'Administrators (not removable)')
        groups.addGroup('Administrators', grp) 
        prm.assignRoleToPrincipal('mypypi.Administrator',
            'groups.Administrators')

        # setup 'Owners' group
        grp =  authentication.PYPIGroup(u'Owners', u'Owners (not removable)')
        groups.addGroup('Owners', grp)
        prm.assignRoleToPrincipal('mypypi.Owner', 'groups.Owners')

        # setup 'Members' group
        grp =  authentication.PYPIGroup(u'Members', u'Members (not removable)')
        groups.addGroup('Members', grp)
        prm.assignRoleToPrincipal('mypypi.Member', 'groups.Members')

        # setup 'Everyone' group for zope.Anonymous
        grp =  authentication.PYPIGroup(u'Everyone', u'Everyone (not removable)')
        groups.addGroup('Everyone', grp)
        sm.registerUtility(grp, IEveryoneGroup)
        # note there is no role grant at site level for groups.Everybody by 
        # default which means the site is not public. Grant a local member role
        # for this group at site level will give read access for anybody

        # setup 'users' member container
        users = UserContainer()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(users))
        auth[u'users'] = users
        auth.authenticatorPlugins += (u'users',)

        # 1. auth plugin for global defined principals
        plugin = PrincipalRegistryAuthenticatorPlugin()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(plugin))
        auth[u'PrincipalRegistryAuthenticatorPlugin'] = plugin
        auth.authenticatorPlugins += (u'PrincipalRegistryAuthenticatorPlugin',)

        # 2. credential plugin for basic auth e.g. XMLRPC or JSON
        cred = HTTPBasicAuthCredentialsPlugin()
        # the realm ``pypi`` is required by distutils. This realm is hardoded
        # in distutils eek
        cred.realm = 'pypi'
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(cred))
        auth[u'HTTPBasicAuthCredentialsPlugin'] = cred
        auth.credentialsPlugins += (u'HTTPBasicAuthCredentialsPlugin',)

        # add FSStorage
        path = getFSStoragePath(confKey='storage')
        fsStorage = FlatPathFSStorage(path)
        fsStorage.fsFileFactory = release.ReleaseFile
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(fsStorage))
        sm['default']['FlatPathFSStorage'] = fsStorage
        sm.registerUtility(fsStorage, IFSStorage)

        # add MirrorJob
        syncJob = job.SyncMirrorPackages()
        self.context.addJob(u'syncMirrorPackages', syncJob)
