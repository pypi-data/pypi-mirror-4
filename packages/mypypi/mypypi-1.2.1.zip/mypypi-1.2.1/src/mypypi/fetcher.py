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
import zope.event
import zope.lifecycleevent
from zope.exceptions.interfaces import DuplicationError

from z3c.configurator import configurator

import mypypi.api
from mypypi.i18n import MessageFactory as _
from mypypi import interfaces
from mypypi import package


class PackageFetcher(object):
    """Package fetcher adapter for site."""

    zope.interface.implements(interfaces.IPackageFetcher)
    zope.component.adapts(interfaces.IPYPISite)

    def __init__(self, context):
        self.context = context

    def getPackage(self, name, pypiURL):
        """Create and returns a mirror package."""
        if name in self.context:
            msg = _('Error: Package with the name, $name, already exist',
                mapping={'name': name})
            mypypi.api.logMirrorError(msg)
            raise DuplicationError(name)
        pkg = package.MirrorPackage(pypiURL)
        newName = pkg.getName(name)
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(pkg))
        self.context[newName] = pkg
        msg = _('Added package: $package', mapping={'package': newName})
        mypypi.api.logMirrorHistory(msg, pypiURL)
        configurator.configure(pkg, None)
        return pkg

    def getPackages(self, names, pypiURL):
        """Create and returns a mirror package collection."""
        pkgNames = mypypi.api.fetchPackageList(pypiURL, names)
        pkgs = []
        keyNames = self.context.keys()
        for name in pkgNames:
            if name in keyNames:
                # skip existing pacakges, we also do not update them
                continue
            pkg = package.MirrorPackage(pypiURL)
            zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(pkg))
            self.context[name] = pkg
            msg = _('Added package: $package', mapping={'package': name})
            mypypi.api.logMirrorHistory(msg, pypiURL)
            configurator.configure(pkg, None)
            pkgs.append(pkg)
        return pkgs

