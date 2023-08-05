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
$Id: __init__.py 841 2007-12-08 02:17:39Z roger.ineichen $
"""

import logging

import zope.component
from zope.intid.interfaces import IIntIds

import z3c.indexer.indexer

from mypypi import interfaces

log = logging.getLogger('mypypi')

def concat(*items):
    return u' '.join([i or u'' for i in items if i is not None])

# IPackage
class PackageIndexer(z3c.indexer.indexer.MultiIndexer):
    """Full text indexer for IPackage."""

    zope.component.adapts(interfaces.IPackage)

    def doIndex(self):
        # package.packageText
        textIndex = self.getIndex('package.packageText')
        text = ' %s' % self.context.__name__ or ''
        textIndex.doIndex(self.oid, text)
        # package.isPublished
        valueIndex = self.getIndex('package.isPublished')
        valueIndex.doIndex(self.oid, self.context.isPublished)
        log.info('Indexing %s %s' % (self.context.__class__.__name__,
            self.context.__name__))

    def doUnIndex(self):
        # package.packageText
        textIndex = self.getIndex('package.packageText')
        textIndex.doUnIndex(self.oid)
        valueIndex = self.getIndex('package.isPublished')
        valueIndex.doUnIndex(self.oid)

    def __repr__(self):
        return '<%s for IPackage>' %self.__class__.__name__


# IRelease
class ReleaseIndexer(z3c.indexer.indexer.MultiIndexer):
    """Full text indexer for IRelease."""

    zope.component.adapts(interfaces.IRelease)

    def __init__(self, context):
        """Registered as named index adapter"""
        super(ReleaseIndexer, self).__init__(context)
        # store the parent package oid, because the __parent__ reference is
        # gone if the transaction manager calls the doUnIndex
        intids = zope.component.getUtility(IIntIds)
        self.packageOID = intids.getId(context.__parent__)

    def doIndex(self):
        # package.releaseText
        textIndex = self.getIndex('package.releaseText')
        sc = self.context
        text = concat(sc.__name__, sc.author, sc.authorEmail, sc.keywords,
                      sc.license, sc.maintainer, sc.maintainerEmail, sc.platform,
                      sc.summary, sc.version)

        # attention, we need to add the package to the index and not the
        # release.
        textIndex.doIndex(self.packageOID, text)

        # release.fullText
        textIndex = self.getIndex('release.fullText')
        textIndex.doIndex(self.oid, text)

        # package.releaseClassifiers
        classifiersIndex = self.getIndex('package.releaseClassifiers')
        if self.context.classifiers:
            text += u' '.join([word for word in self.context.classifiers])
        # attention, we need to add the package to the index and not the
        # release.
        classifiersIndex.doIndex(self.packageOID, text)
        log.info('Indexing %s %s' % (self.context.__class__.__name__,
            self.context.__name__))

    def doUnIndex(self):
        # package.releaseText
        textIndex = self.getIndex('package.releaseText')
        textIndex.doUnIndex(self.packageOID)
        # package.releaseClassifiers
        classifiersIndex = self.getIndex('package.releaseClassifiers')
        classifiersIndex.doUnIndex(self.packageOID)
        # release.fullText
        textIndex = self.getIndex('release.fullText')
        textIndex.doUnIndex(self.oid)

    def __repr__(self):
        return '<%s for IRelease>' %self.__class__.__name__


# IPYPIUser
class PYPIUserIndexer(z3c.indexer.indexer.MultiIndexer):
    """Full text indexer for IPYPIUser."""

    zope.component.adapts(interfaces.IPYPIUser)

    def doIndex(self):
        # user.fullText
        textIndex = self.getIndex('user.fullText')
        sc = self.context
        text = concat(sc.login, sc.title, sc.description, sc.firstName,
                      sc.lastName, sc.email)
        textIndex.doIndex(self.oid, text)
        log.info('Indexing %s %s' % (self.context.__class__.__name__,
            self.context.__name__))

    def doUnIndex(self):
        # user.fullText
        textIndex = self.getIndex('user.fullText')
        textIndex.doUnIndex(self.oid)

    def __repr__(self):
        return '<%s for IPYPIUser>' %self.__class__.__name__


# IHistoryEntry
class HistoryEntryIndexer(z3c.indexer.indexer.MultiIndexer):
    """Full text indexer for IHistoryEntry."""

    zope.component.adapts(interfaces.IHistoryEntry)

    def doIndex(self):
        # historyEntry.fullText
        textIndex = self.getIndex('historyEntry.fullText')
        textIndex.doIndex(self.oid, self.context.message)
        log.info('Indexing %s %s' % (self.context.__class__.__name__,
            self.context.__name__))

    def doUnIndex(self):
        # historyEntry.fullText
        textIndex = self.getIndex('historyEntry.fullText')
        textIndex.doUnIndex(self.oid)

    def __repr__(self):
        return '<%s for IHistoryEntry>' %self.__class__.__name__


# IErrorEntry
class ErrorEntryIndexer(z3c.indexer.indexer.MultiIndexer):
    """Full text indexer for IErrorEntry."""

    zope.component.adapts(interfaces.IErrorEntry)

    def doIndex(self):
        # errorEntry.fullText
        textIndex = self.getIndex('errorEntry.fullText')
        textIndex.doIndex(self.oid, self.context.message)
        log.info('Indexing %s %s' % (self.context.__class__.__name__,
            self.context.__name__))

    def doUnIndex(self):
        # errorEntry.fullText
        textIndex = self.getIndex('errorEntry.fullText')
        textIndex.doUnIndex(self.oid)

    def __repr__(self):
        return '<%s for IErrorEntry>' %self.__class__.__name__
