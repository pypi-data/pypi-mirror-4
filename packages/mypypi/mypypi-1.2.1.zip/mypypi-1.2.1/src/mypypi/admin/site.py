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
import zope.i18n
import zope.schema
from zope.index.text import parsetree

import z3c.tabular.table
from z3c.table import column
from z3c.form import field
from z3c.form import button
from z3c.formui import form
from z3c.indexer.query import TextQuery
from z3c.indexer.search import SearchQuery
from z3c.template.template import getPageTemplate

import mypypi.api
from mypypi import interfaces
from mypypi.admin import PublishedColumn
from mypypi.i18n import MessageFactory as _
from mypypi.exceptions import PackageError


class EditForm(form.EditForm):

    template = getPageTemplate(name='simple')

    label = _('Edit Site')

    fields = field.Fields(interfaces.IPYPISite).select('title',
        'checkClassifiersOnVerify', 'checkClassifiersOnUpload')


class ITextSearchForm(zope.interface.Interface):
    """Member search filter form."""

    searchText = zope.schema.TextLine(
        title=_('Search text'),
        description=_('The search text.'),
        default=u"",
        required=False)


class PackageNameColumn(column.LinkColumn):
    """Package column."""

    header = _('Package')
    linkName = 'releases.html'

    def getLinkContent(self, item):
        """Setup link content."""
        return item.__name__


class PackageMirrorColumn(column.Column):
    """Mirror column."""

    header = _('Mirror')

    def renderCell(self, item):
        if interfaces.IMirrorPackage.providedBy(item):
            return zope.i18n.translate(_('Yes'), context=self.request)
        else:
            return zope.i18n.translate(_('No'), context=self.request)


class SourceColumn(column.LinkColumn):
    """Source link column."""

    header = _('Source')

    def getLinkURL(self, item):
        """Setup link url."""
        if interfaces.IMirrorPackage.providedBy(item):
            return item.pypiURL
        return '#'

    def getLinkContent(self, item):
        """Setup link content."""
        if interfaces.IMirrorPackage.providedBy(item):
            return zope.i18n.translate(_('link'), context=self.request)
        return ''


class Packages(z3c.tabular.table.DeleteFormTable):
    """Package management page."""

    zope.interface.implements(interfaces.IPackageManagementPage)

    buttons = z3c.tabular.table.DeleteFormTable.buttons.copy()
    handlers = z3c.tabular.table.DeleteFormTable.handlers.copy()

    label = _('Packages')
    formErrorsMessage = _('There were some errors.')
    updateNoItemsMessage = _('No items selected for update')
    ignoreContext = True
    errors  = []

    batchSize = 500
    startBatchingAt = 500

    fields = field.Fields(ITextSearchForm)

    def setUpColumns(self):
        return [
            column.addColumn(self, column.CheckBoxColumn, u'checkbox',
                             weight=1, cssClasses={'th':'firstColumnHeader'}),
            column.addColumn(self, PackageMirrorColumn, u'mirror',
                             weight=2),
            column.addColumn(self, PublishedColumn, u'published',
                             weight=3),
            column.addColumn(self, PackageNameColumn, u'__name__',
                             weight=4),
            column.addColumn(self, SourceColumn, u'source',
                             weight=5),
            column.addColumn(self, column.CreatedColumn, name=u'created',
                             weight=6, header=u'Created'),
            column.addColumn(self, column.ModifiedColumn, name=u'modified',
                             weight=7, header=u'Modified')
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
                ptQuery = TextQuery('package.packageText', searchText)
                rtQuery = TextQuery('package.releaseText', searchText)
                rcQuery = TextQuery('package.releaseClassifiers', searchText)
                return SearchQuery(ptQuery).Or(rtQuery).Or(
                    rcQuery).searchResults()
            except parsetree.ParseError, error:
                self.status = _('Invalid search text.')
                # Return an empty set, since an error must have occurred
                return []

        return self.context.values()

        # only show obj which we have permission for
        return [obj for obj in values if mypypi.api.checkViewPermission(obj)]

    def executeDelete(self, item):
        del self.context[item.__name__]

    def update(self):
        super(Packages, self).update()
        self.publishedItems = [item for item in self.values if item.published]

    @button.buttonAndHandler(u'Synchronize All', name='synchronizeAll',
        condition=lambda form: mypypi.api.checkManagePackagesPermission(form))
    def handleSyncPackages(self, action):
        """Update all packages."""
        self.context.syncMirrorPackages()
        self.status = _('Packages sucessfuly updated')

    @button.buttonAndHandler(u'Synchronize Selected', name='synchronizePkgs',
        condition=lambda form: mypypi.api.checkManagePackagesPermission(form))
    def handleUpdate(self, action):
        """Update the selected packages."""
        if not len(self.selectedItems):
            self.status = self.updateNoItemsMessage
            return
        # reset error list for catch new errors
        self.errors = []
        for pkg in self.selectedItems:
            try:
                if interfaces.IMirrorPackage.providedBy(pkg):
                    pkg.update()
                else:
                    self.errors.append(
                        "Can't sync/update LocalPackage %s only "
                        "MirrorPackage can get synced" % pkg.__name__)
            except PackageError, e:
                self.errors.append('%s (%s)' % (pkg.__name__, e))
        if self.errors:
            self.status = _('Could not update the following packages')

    @button.buttonAndHandler(u'Set Published state', name='publish',
        condition=lambda form: mypypi.api.checkManagePackagesPermission(form))
    def _handlePublish(self, action):
        """Publish all selected release files."""
        for item in self.values:
            if item in self.publishedItems:
                mypypi.api.markItemsAsPublished(item, True)
            else:
                mypypi.api.markItemsAsPublished(item, False)
        # update the table rows before we start with rendering
        self.updateAfterActionExecution()

    @button.buttonAndHandler(u'Search', name='search',
        condition=lambda form: mypypi.api.checkViewPermission(form))
    def handleSearch(self, action):
        # just offer a button and do nothing, we search anyway, see values()
        pass


class NameColumn(column.Column):
    """NameColumn (counter) column."""

    header = _('ID')

    def renderCell(self, item):
        """render comment."""
        return item.__name__


class UserNameColumn(column.Column):
    """NameColumn (counter) column."""

    header = _('User')

    def renderCell(self, item):
        """render username."""
        return item.userName


class LoggerMirrorColumn(column.Column):
    """Mirror column."""

    header = _('Mirror')

    def renderCell(self, item):
        if interfaces.IMirrorLogger.providedBy(item):
            return zope.i18n.translate(_('Yes'), context=self.request)
        else:
            return zope.i18n.translate(_('No'), context=self.request)


class MessageColumn(column.Column):
    """Message column."""

    header = _('Messages')

    def _renderContent(self, logger, entry):
        msg = zope.i18n.translate(entry.message, context=self.request)
        if interfaces.IMirrorLogger.providedBy(logger):
            linkImg = u'[>>]'
            path = entry.path
            linkTemplate = '<a href="%s" title="%s" target="_blank">%s</a>'
            return '%s&nbsp;&nbsp; %s' % (linkTemplate % (path, path, linkImg),
                linkTemplate % (path, path, msg))
        else:
            return msg

    def renderCell(self, item):
        """Translate and render the messages."""
        values = sorted(item.values(), key=lambda x:int(x.__name__))
        msgs = [self._renderContent(item ,entry) for entry in values]
        return u'<br />'.join(msgs)


class History(z3c.tabular.table.DeleteFormTable):
    """History page."""

    zope.interface.implements(interfaces.IHistoryManagementPage)

    buttons = z3c.tabular.table.DeleteFormTable.buttons.copy()
    handlers = z3c.tabular.table.DeleteFormTable.handlers.copy()

    label = _('History')
    formErrorsMessage = _('There were some errors.')
    ignoreContext = True
    errors  = []
    # supress table sorting
    sortOn = None

    fields = field.Fields(ITextSearchForm)

    def setUpColumns(self):
        return [
           column.addColumn(self, column.CheckBoxColumn, name=u'checkbox',
                             weight=1, cssClasses={'th':'firstColumnHeader'}),
           column.addColumn(self, NameColumn, u'name',
                             weight=2),
           column.addColumn(self, column.CreatedColumn, name=u'created',
                             weight=3, header=_(u'Created')),
           column.addColumn(self, UserNameColumn, name=u'username',
                             weight=4),
           column.addColumn(self, LoggerMirrorColumn, u'mirror',
                             weight=5),
           column.addColumn(self, MessageColumn, u'comment',
                             weight=6),
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
                historyQuery = TextQuery('historyEntry.fullText', searchText)
                errorQuery = TextQuery('errorEntry.fullText', searchText)
                return SearchQuery(historyQuery).Or(errorQuery).searchResults()
            except parsetree.ParseError, error:
                self.status = _('Invalid search text.')
                # Return an empty set, since an error must have occurred
                return []

        values = sorted(interfaces.ILogContainer(self.context).values(),
            key=lambda x:int(x.__name__))
        values.reverse()
        return values

    def executeDelete(self, item):
        container = interfaces.ILogContainer(self.context)
        del container[item.__name__]

    @button.buttonAndHandler(u'Search', name='search')
    def handleSearch(self, action):
        # just offer a button and do nothing, we search anyway, see values()
        pass
