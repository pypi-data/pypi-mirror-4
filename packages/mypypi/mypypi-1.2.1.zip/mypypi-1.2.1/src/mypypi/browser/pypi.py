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

import zope.component
from zope.publisher.interfaces import NotFound
from zope.publisher.browser import BrowserPage
from zope.traversing.browser import absoluteURL
from zope.component import hooks

from z3c.table import table
from z3c.table import column
from z3c.template.template import getPageTemplate
from z3c.template.template import getLayoutTemplate

import mypypi.api
from mypypi import interfaces


class PackageTraverser(BrowserPage):
    """Allows to traverse to latest or given relase."""

    zope.interface.implements(interfaces.IPYPIPage)

    def publishTraverse(self, request, name):
        # make the pypi view act as a traversable name
        # this allows us to traverse to the pkg
        pkg = self.context.get(name)
        if pkg is None or not pkg.isPublished:
            raise NotFound(self, name, request)
        # get the index view from this package
        view = None
        view = zope.component.queryMultiAdapter((pkg, request), name='pypi')
        if view is None:
            raise NotFound(self, name, request)
        return view

    def __call__(self):
        # get the view for the latest release from this package
        view = None
        if self.context.latest is not None and self.context.latest.isPublished:
            view = zope.component.queryMultiAdapter((self.context.latest,
                self.request), name='pypi')
        if view is None:
            raise NotFound(self.context, '', self.request)
        # call and return
        return view()


class UpdatedColumn(column.ModifiedColumn):
    """Updated column."""

    formatterCategory = u'dateTime'
    formatterLength = u'short'
    attrName = 'modified'


class PackageColumn(column.LinkColumn):
    """Updated column."""

    def getLinkURL(self, item):
        """Setup link url."""
        latest = item.latest
        if latest is not None:
            site = hooks.getSite()
            return '%s/pypi/%s/%s' % (absoluteURL(site, self.request), item.__name__,
                item.latest.__name__)
        return '%s/pypi/%s' % (absoluteURL(site, self.request), item.__name__)

    def getLinkContent(self, item):
        latest = item.latest
        if latest is not None:
            return '%s %s' % (item.__name__, latest.__name__)
        return item.__name__


class DescriptionColumn(column.Column):
    """Updated column."""

    def renderCell(self, item):
        latest = item.latest
        if latest is not None:
            return latest.summary


class PYPIIndex(table.Table):
    """PyPi (package links) index."""

    zope.interface.implements(interfaces.IPYPIPage)

    layout = getLayoutTemplate('pypi')
    template = getPageTemplate()

    cssClasses = {'table':'contents'}
    cssClassEven = u'even'
    cssClassOdd = u'odd'

    sortOn = 1

    def publishTraverse(self, request, name):
        # this allows us to traverse to the search page
        if name == 'search.html':
            return zope.component.getMultiAdapter((self, request),
                name=name)
        # make this view traversable, this allows us to traverse to the pkg
        pkg = self.context.get(name)
        if pkg is None or not pkg.isPublished:
            raise NotFound(self, name, request)
        # get the view for the latest release from this package
        view = None
        traverser = zope.component.queryMultiAdapter((pkg, request), name='pypi')
        if traverser is None:
            raise NotFound(self, name, request)
        return traverser

    def setUpColumns(self):
        return [
           column.addColumn(self, UpdatedColumn, name=u'updated',
                             weight=1, header=u'Updated'),
           column.addColumn(self, PackageColumn, name=u'package',
                             weight=2, header=u'Package'),
           column.addColumn(self, DescriptionColumn, name=u'description',
                             weight=3, header=u'Description'),
            ]

    @property
    def values(self):
        # only show obj which we have permission for and which get published
        return [pkg for pkg in self.context.values()
                if mypypi.api.checkViewPermission(pkg) and pkg.isPublished]

    def render(self):
        return self.template()


class FileColumn(column.LinkColumn):
    """Updated column."""

    def getLinkURL(self, item):
        """Setup link url."""
        if item.md5Digest is not None:
            return '%s#md5=%s' % (absoluteURL(item, self.request), item.md5Digest)
        else:
            return absoluteURL(item, self.request)

    def getLinkContent(self, item):
        return item.__name__


class TypeColumn(column.Column):
    """Updated column."""

    def renderCell(self, item):
        return item.packageType


class PythonVersionColumn(column.Column):
    """Updated column."""

    def renderCell(self, item):
        return item.pythonVersion


class SizeColumn(column.Column):
    """Updated column."""

    def renderCell(self, item):
        return item.size


class DownloadsColumn(column.Column):
    """Updated column."""

    def renderCell(self, item):
        return item.downloads


class PYPIRelease(table.Table):
    """PyPi (release links) page."""

    zope.interface.implements(interfaces.IPYPIPage)

    layout = getLayoutTemplate('pypi')
    template = getPageTemplate()

    cssClasses = {'table':'contents'}
    cssClassEven = u'even'
    cssClassOdd = u'odd'

    sortOn = 0

    @property
    def name(self):
        return '%s %s' % (self.context.__parent__.__name__,
            self.context.__name__)

    @property
    def description(self):
        return mypypi.api.formatDescription(self.context.description)

    @property
    def classifiers(self):
        return []

    def setUpColumns(self):
        return [
           column.addColumn(self, FileColumn, name=u'file',
                             weight=1, header=u'File'),
           column.addColumn(self, TypeColumn, name=u'type',
                             weight=2, header=u'Type'),
           column.addColumn(self, PythonVersionColumn, name=u'version',
                             weight=3, header=u'Py Version'),
           column.addColumn(self, SizeColumn, name=u'size',
                             weight=4, header=u'Size'),
           column.addColumn(self, DownloadsColumn, name=u'downloads',
                             weight=5, header=u'# downloads'),
            ]

    @property
    def values(self):
        # only show obj which we have permission for and which get published
        return [obj for obj in self.context.values()
                if mypypi.api.checkViewPermission(obj) and obj.isPublished]

    def render(self):
        return self.template()
