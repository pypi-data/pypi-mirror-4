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
from zope.exceptions.interfaces import DuplicationError
from zope.traversing.browser import absoluteURL

from z3c.configurator import configurator
import z3c.tabular.table
from z3c.table import column
from z3c.form import field
from z3c.form import button
from z3c.form.browser.textlines import TextLinesFieldWidget
from z3c.formui import form
from z3c.template.template import getPageTemplate

import p01.fsfile.schema
import p01.fsfile.browser

import mypypi.api
from mypypi.i18n import MessageFactory as _
from mypypi import interfaces
from mypypi import release
from mypypi.admin import PublishedColumn


class LocalReleaseAddForm(form.AddForm):

    template = getPageTemplate(name='simple')

    buttons = form.AddForm.buttons.copy()
    handlers = form.AddForm.handlers.copy()

    label = _('Add Local Release')

    fields = field.Fields(interfaces.ILocalRelease).select(
        '__name__')

    def createAndAdd(self, data):
        try:
            # create
            self.contentName = data['__name__']
            obj = release.LocalRelease()

            # notify
            zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))

            # add the release
            self.context[self.contentName] = obj

            # configure
            configurator.configure(obj, data)

            self._finishedAdd = True
            return obj

        except DuplicationError, e:
            self.status = _('Package with the same name already exist.')
            transaction.doom()
            return


    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.getURL())

    def nextURL(self):
        context = self.context[self.contentName]
        return '%s/files.html' % absoluteURL(context, self.request)


class MirrorReleaseAddForm(form.AddForm):

    template = getPageTemplate(name='simple')

    buttons = form.AddForm.buttons.copy()
    handlers = form.AddForm.handlers.copy()

    label = _('Add Mirror Release')

    fields = field.Fields(interfaces.IMirrorRelease).select(
        '__name__')

    def createAndAdd(self, data):
        try:
            # create
            self.contentName = data['__name__']
            obj = release.MirrorRelease()

            # notify
            zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))

            # add the release
            self.context[self.contentName] = obj

            # configure
            configurator.configure(obj, data)

            self._finishedAdd = True
            return obj

        except DuplicationError, e:
            self.status = _('Mirror package with the same name already exist.')
            return

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.getURL())

    def nextURL(self):
        context = self.context[self.contentName]
        return '%s/files.html' % absoluteURL(context, self.request)


MULTIFIELDS = ('classifiers', 'obsoletes', 'provides', 'requires')


class LocalReleaseEditForm(form.EditForm):

    template = getPageTemplate(name='simple')

    label = _('Edit Local Release')

    fields = field.Fields(interfaces.IRelease).omit('__parent__', 'version')

    #here we go again... no multiwidget yet in z3c.form 1.9
    def __init__(self, context, request):
        for f in MULTIFIELDS:
            self.fields[f].widgetFactory = TextLinesFieldWidget

        super(LocalReleaseEditForm, self).__init__(context, request)


class MirrorReleaseEditForm(form.EditForm):

    template = getPageTemplate(name='simple')

    label = _('Edit Mirror Release')

    fields = field.Fields(interfaces.IRelease).select('published')


class MirrorColumn(column.Column):
    """Mirror column."""

    header = _('Mirror')

    def renderCell(self, item):
        if interfaces.IMirrorRelease.providedBy(item.__parent__):
            return zope.i18n.translate(_('Yes'), context=self.request)
        else:
            return zope.i18n.translate(_('No'), context=self.request)


class SourceColumn(column.LinkColumn):
    """Source link column."""

    header = _('Source')

    def getLinkURL(self, item):
        """Setup link url."""
        return item.url

    def getLinkContent(self, item):
        """Setup link content."""
        return zope.i18n.translate(_('link'), context=self.request)

    def renderCell(self, item):
        if interfaces.IMirrorRelease.providedBy(item.__parent__):
            #can happen that we manually add a file into a MirrorRelease...
            #in that case url will be None
            if item.url is not None:
                return super(SourceColumn, self).renderCell(item)
        return ''


class ReleaseFiles(z3c.tabular.table.DeleteFormTable):
    """Release file management page."""

    zope.interface.implements(interfaces.IReleaseFileManagementPage)

    buttons = z3c.tabular.table.DeleteFormTable.buttons.copy()
    handlers = z3c.tabular.table.DeleteFormTable.handlers.copy()

    formErrorsMessage = _('There were some errors.')
    ignoreContext = True
    errors  = []

    batchSize = 100
    startBatchingAt = 100

    def setUpColumns(self):
        return [
            column.addColumn(self, column.CheckBoxColumn, u'checkbox',
                             weight=1, cssClasses={'th':'firstColumnHeader'}),
            column.addColumn(self, MirrorColumn, u'mirror',
                             weight=2),
            column.addColumn(self, PublishedColumn, u'published',
                             weight=3),
            column.addColumn(self, column.LinkColumn, u'__name__',
                             weight=4),
            column.addColumn(self, SourceColumn, u'source',
                             weight=5),
            column.addColumn(self, column.CreatedColumn, name=u'created',
                             weight=6, header=u'Created'),
            column.addColumn(self, column.ModifiedColumn, name=u'modified',
                             weight=7, header=u'Modified')
            ]

    @property
    def label(self):
        return _('Release File Management for $releaseName',
            mapping={'releaseName': self.context.__name__})

    @property
    def values(self):
        """Setup release as values."""
        # only show obj which we have permission for
        return [obj for obj in self.context.values()
                if mypypi.api.checkViewPermission(obj)]

    @property
    def isMirrorRelease(self):
        return interfaces.IMirrorRelease.providedBy(self.context)

    @property
    def hint(self):
        if len(self.context) == 0:
            if self.isMirrorRelease:
                return _(u'This release has no files. '
                          u'Try first the Fetch all button. '
                          u'If it fails, use the add menu to add files.')
            else:
                return _(u'This release has no files, use the add menu to add files')
        else:
            return ''

    def executeDelete(self, item):
        del self.context[item.__name__]

    def updateAfterActionExecution(self):
        """Update table data if subform changes soemthing."""
        # first update table data which probably changed
        super(ReleaseFiles, self).updateAfterActionExecution()
        self.publishedItems = [item for item in self.values if item.published]

    def update(self):
        self.publishedItems = [item for item in self.values if item.published]
        super(ReleaseFiles, self).update()

    @button.buttonAndHandler(u'Set Published state', name='publish')
    def _handlePublish(self, action):
        """Publish all selected release files."""
        for item in self.values:
            if item in self.publishedItems:
                mypypi.api.markItemsAsPublished(item, True)
            else:
                mypypi.api.markItemsAsPublished(item, False)
        # update the table rows before we start with rendering
        self.updateAfterActionExecution()

    @button.buttonAndHandler(u'Fetch all', name='fetchAll',
        condition=lambda form: form.isMirrorRelease)
    def _handleFetchAll(self, action):
        """fetch all packages from mirror."""
        self.context.update()
        # update the table rows before we start with rendering
        self.updateAfterActionExecution()



# setup IReleaseFile storage lookup
class IReleaseFileUploadSchema(zope.interface.Interface):
    """Release file upload schema."""

    upload = p01.fsfile.schema.FSFileUpload(
        title=_(u'Release File'),
        description=_('The release file distribution.'),
        fsStorageName=u'',
        fsNameSpace=u'upload', # use upload storage
        allowEmptyPostfix=False,
        required=True)


class ReleaseFileAddForm(form.AddForm):

    template = getPageTemplate(name='simple')

    buttons = form.AddForm.buttons.copy()
    handlers = form.AddForm.handlers.copy()

    label = _('Add Release file')

    fields = field.Fields(IReleaseFileUploadSchema)

    def createAndAdd(self, data):
        try:
            # create
            releaseFile = data['upload']

            # notify
            zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(
                releaseFile))

            # add the release file
            self.context[releaseFile.__name__] = releaseFile

            self._finishedAdd = True
            return releaseFile

        except DuplicationError, e:
            self.status = _('Release file with the same name already exists.')
            return

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.getURL())

    def nextURL(self):
        return '%s/files.html' % absoluteURL(self.context, self.request)


class ReleaseFileEditForm(form.EditForm):

    template = getPageTemplate(name='simple')

    label = _('Edit Release File')

    fields = field.Fields(interfaces.IReleaseFile).select('published')


class ReleaseFileDownload(p01.fsfile.browser.FSFileDownload):
    """Release file download."""

    def __call__(self):
        return super(ReleaseFileDownload, self).__call__()
