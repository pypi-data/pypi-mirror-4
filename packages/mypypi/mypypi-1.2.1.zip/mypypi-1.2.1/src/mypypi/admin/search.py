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
import zope.schema
from zope.index.text import parsetree
from zope.traversing.browser import absoluteURL

import z3c.tabular.table
from z3c.table import column
from z3c.form import field
from z3c.form import button
from z3c.indexer.query import TextQuery
from z3c.indexer.query import Eq
from z3c.indexer.search import SearchQuery
from z3c.template.template import getPageTemplate
from z3c.template.template import getLayoutTemplate

from mypypi.i18n import MessageFactory as _
from mypypi import interfaces


class ITextSearchForm(zope.interface.Interface):
    """Member search filter form."""

    searchText = zope.schema.TextLine(
        title=_('Search text'),
        description=_('The search text.'),
        default=u"",
        required=False)


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
            return absoluteURL(latest, self.request)
        return absoluteURL(item, self.request)

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


class SearchResult(z3c.tabular.table.FormTable):
    """Search result page."""

    template = getPageTemplate()

    buttons = z3c.tabular.table.FormTable.buttons.copy()
    handlers = z3c.tabular.table.FormTable.handlers.copy()

    label = _('Search result')
    formErrorsMessage = _('There were some errors.')
    ignoreContext = True
    errors  = []
    prefix = 'search'

    fields = field.Fields(ITextSearchForm)

    sortOn = 1

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
        """Setup search values."""
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return []
        searchText = data.get('searchText')
        if searchText:
            try:
                pkgQuery = TextQuery('package.packageText', searchText)
                releaseQuery = TextQuery('package.releaseText', searchText)
                classifierQuery = TextQuery('package.releaseClassifiers',
                    searchText)
                return SearchQuery(pkgQuery).Or(releaseQuery).Or(
                    classifierQuery).searchResults()
            except parsetree.ParseError, error:
                self.status = _('Invalid search text.')
                # Return an empty set, since an error must have occurred
                return []

        return self.context.values()

    @button.buttonAndHandler(u'Search', name='search')
    def handleSearch(self, action):
        # just offer a button and do nothing, we search anyway, see values()
        pass

    def render(self):
        return self.template()


class PYPIIndexSearchPackageColumn(column.LinkColumn):
    """Updated column."""

    def getLinkURL(self, item):
        """Setup link url."""
        site = item.__parent__
        baseURL = absoluteURL(site, self.request)
        latest = item.latest
        if latest is not None:
            return '%s/pypi/%s/%s' % (baseURL, item.__name__, latest.__name__)
        return '%s/pypi/%s' % (baseURL, item.__name__)

    def getLinkContent(self, item):
        latest = item.latest
        if latest is not None:
            return '%s %s' % (item.__name__, latest.__name__)
        return item.__name__


class PYPIIndexSearchResult(SearchResult):
    """PYPI index search result page."""

    zope.interface.implements(interfaces.IPYPIPage)

    def setUpColumns(self):
        return [
           column.addColumn(self, UpdatedColumn, name=u'updated',
                             weight=1, header=u'Updated'),
           column.addColumn(self, PYPIIndexSearchPackageColumn, name=u'package',
                             weight=2, header=u'Package'),
           column.addColumn(self, DescriptionColumn, name=u'description',
                             weight=3, header=u'Description'),
            ]

    @property
    def values(self):
        """Setup search values."""
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return []
        searchText = data.get('searchText')
        if searchText:
            try:
                pkgQuery = TextQuery('package.packageText', searchText)
                releaseQuery = TextQuery('package.releaseText', searchText)
                classifierQuery = TextQuery('package.releaseClassifiers',
                    searchText)
                isPublishedQuery = Eq('package.isPublished', True)
                return SearchQuery(pkgQuery).Or(releaseQuery).Or(
                    classifierQuery).And(isPublishedQuery).searchResults()
            except parsetree.ParseError, error:
                self.status = _('Invalid search text.')
                # Return an empty set, since an error must have occurred
                return []

        return [pkg for pkg in self.context.context.values() if pkg.isPublished]
