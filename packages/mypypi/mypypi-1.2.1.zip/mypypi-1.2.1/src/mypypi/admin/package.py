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

import transaction
import zope.interface
import zope.schema
from zope.exceptions.interfaces import DuplicationError
from zope.traversing.browser import absoluteURL
from zope.component import hooks

from z3c.configurator import configurator
import z3c.tabular.table
from z3c.table import column
from z3c.form import field
from z3c.form import button
from z3c.form.browser.textlines import TextLinesFieldWidget
from z3c.formui import form
from z3c.template.template import getPageTemplate

import mypypi.api
from mypypi.i18n import MessageFactory as _
from mypypi import interfaces
from mypypi import package
from mypypi.admin import PublishedColumn
from mypypi.exceptions import PackageError
from mypypi.exceptions import MissingReleases


class LocalPackageAddForm(form.AddForm):

    template = getPageTemplate(name='simple')

    buttons = form.AddForm.buttons.copy()
    handlers = form.AddForm.handlers.copy()

    label = _('Add LocalPackage')

    fields = field.Fields(interfaces.ILocalPackage).select(
        '__name__')

    def createAndAdd(self, data):
        try:
            # create
            self.contentName = data['__name__']
            obj = package.LocalPackage()

            # notify
            zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))

            # add the package
            self.context[self.contentName] = obj

            # configure
            configurator.configure(obj, data)
            msg = _('Local package $name added',
                mapping={'name': self.contentName})
            mypypi.api.logLocalHistory(msg)

            self._finishedAdd = True
            return obj

        except DuplicationError, e:
            self.status = _('Package with the same name already exist.')
            return

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.getURL())

    def nextURL(self):
        context = self.context[self.contentName]
        return '%s/releases.html' % absoluteURL(context, self.request)


class MirrorPackageAddForm(form.AddForm):

    template = getPageTemplate(name='simple')

    buttons = form.AddForm.buttons.copy()
    handlers = form.AddForm.handlers.copy()

    label = _('Add MirrorPackage')

    fields = field.Fields(interfaces.IMirrorPackage).select(
        '__name__', 'pypiURL')

    def createAndAdd(self, data):
        __name__ = data['__name__']
        pypiURL = data['pypiURL']
        try:
            # get package fetcher
            site = hooks.getSite()
            fetcher = interfaces.IPackageFetcher(site)
            # create, add and configure package
            pkg = fetcher.getPackage(__name__, pypiURL)

        except (DuplicationError, KeyError), e:
            self.status = _("Package with the same name already exist.")
            return

        except MissingReleases, e:
            self.status = _("No release found for the package '%s'. Make sure "
                            "the package and at least one release does exist "
                            "at the given index url" % __name__)
            # remove the package and do not doom the transaction
            del self.context[__name__]
            return

        except PackageError, e:
            transaction.doom()
            self.status = str(e)
            return

        self._finishedAdd = True
        return pkg

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.getURL())

    def nextURL(self):
        return '%s/packages.html' % absoluteURL(self.context, self.request)


class IMirrorPackageCollectionSchema(zope.interface.Interface):
    """MirrorPackage batch."""

    packageNames = zope.schema.List(
        title=_(u'Package names (* is allowed as placeholder)'),
        description=_(u'Package names'),
        value_type=zope.schema.TextLine(
            title=_(u'Package name'),
            description=_(u'Package name'),
            required=True
            ),
        default=[],
        required=False)

    pypiURL = zope.schema.URI(
        title=_(u'PyPi URL'),
        description=_(u'PyPi URL'),
        default='http://pypi.python.org/pypi',
        required=True)


class MirrorPackageCollectionForm(form.EditForm):

    template = getPageTemplate(name='simple')

    ignoreContext = True
    nextURL = None

    label = _('Add MirrorPackage Collection')

    fields = field.Fields(IMirrorPackageCollectionSchema).select(
        'packageNames', 'pypiURL')

    fields['packageNames'].widgetFactory = TextLinesFieldWidget

    @button.buttonAndHandler(u'Add Package Collection')
    def _addPackageHandler(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        pkgNames = data['packageNames']
        pypiURL = data['pypiURL']
        try:
            # get package fetcher
            site = hooks.getSite()
            fetcher = interfaces.IPackageFetcher(site)
            # create, add and configure packages
            pkgs = fetcher.getPackages(pkgNames, pypiURL)
            if not pkgs:
                self.status = _('No new package was added')
                return

        except PackageError, e:
            transaction.doom()
            self.status = str(e)
            return

        except DuplicationError, e:
            transaction.doom()
            self.status = _("A package with the same name already exist.")
            return

        self.nextURL = '%s/packages.html' % absoluteURL(self.context,
            self.request)

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.nextURL = self.request.getURL()

    def render(self):
        if self.nextURL is not None:
            self.request.response.redirect(self.nextURL)
        return super(MirrorPackageCollectionForm, self).render()


class LocalPackageEditForm(form.EditForm):

    template = getPageTemplate(name='simple')

    label = _('Edit LocalPackage')

    fields = field.Fields(interfaces.ILocalPackage).select('__name__',
        'published')


class MirrorPackageEditForm(form.EditForm):

    template = getPageTemplate(name='simple')

    label = _('Edit MirrorPackage')

    fields = field.Fields(interfaces.IMirrorPackage).select('__name__',
        'published')


class ReleaseNameColumn(column.LinkColumn):
    """Release column."""

    header = _('Release')
    linkName = 'files.html'

    def getLinkContent(self, item):
        """Setup link content."""
        return item.__name__


class SourceColumn(column.LinkColumn):
    """Source link column."""

    header = _('Source')

    def getLinkURL(self, item):
        """Setup link url."""
        if interfaces.IMirrorRelease.providedBy(item):
            return item.url
        return u''

    def getLinkContent(self, item):
        """Setup link content."""
        if interfaces.IMirrorRelease.providedBy(item):
            return zope.i18n.translate(_('link'), context=self.request)
        return u''


class MirrorColumn(column.Column):
    """Mirror column."""

    header = _('Mirror')

    def renderCell(self, item):
        if interfaces.IMirrorRelease.providedBy(item):
            return zope.i18n.translate(_('Yes'), context=self.request)
        else:
            return zope.i18n.translate(_('No'), context=self.request)

class FileCountColumn(column.Column):
    """File count column."""

    header = _('Files')

    def renderCell(self, item):
        cnt = len(item)
        if cnt == 0:
            #no files in the release just causes problems
            return '<span class="redBack">&nbsp;%s&nbsp;</span>' % cnt
        else:
            return str(cnt)


class Releases(z3c.tabular.table.DeleteFormTable):
    """Release management page."""

    zope.interface.implements(interfaces.IReleaseManagementPage)

    buttons = z3c.tabular.table.DeleteFormTable.buttons.copy()
    handlers = z3c.tabular.table.DeleteFormTable.handlers.copy()

    formErrorsMessage = _('There were some errors.')
    updateNoItemsMessage = _('No items selected for update')
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
            column.addColumn(self, ReleaseNameColumn, u'__name__',
                             weight=4),
            column.addColumn(self, FileCountColumn, u'files',
                             weight=5),
            column.addColumn(self, SourceColumn, u'source',
                             weight=6),
            column.addColumn(self, column.CreatedColumn, name=u'created',
                             weight=7, header=u'Created'),
            column.addColumn(self, column.ModifiedColumn, name=u'modified',
                             weight=8, header=u'Modified')
            ]

    @property
    def label(self):
        return _('Release Management for $packageName',
            mapping={'packageName': self.context.__name__})

    @property
    def values(self):
        """Setup release as values."""
        # only show obj which we have permission for
        return [obj for obj in self.context.values()
                if mypypi.api.checkViewPermission(obj)]

    @property
    def isMirrorPackage(self):
        return interfaces.IMirrorPackage.providedBy(self.context)

    def executeDelete(self, item):
        del self.context[item.__name__]

    def update(self):
        super(Releases, self).update()
        self.publishedItems = [item for item in self.values if item.published]

    @button.buttonAndHandler(u'Update', name='updatePackage',
        condition=lambda form: form.isMirrorPackage)
    def _handleUpdate(self, action):
        """Update the selected release."""
        if not len(self.selectedItems):
            self.status = self.updateNoItemsMessage
            return
        # reset error list for catch new errors
        self.errors = []
        for obj in self.selectedItems:
            try:
                obj.update()
            except PackageError, e:
                self.errors.append('%s (%s)' % (obj.__name__, e))
        if self.errors:
            self.status = _('Could not update the following releases')

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
        condition=lambda form: form.isMirrorPackage)
    def _handleFetchAll(self, action):
        """fetch all packages from mirror."""
        self.context.update()
        # update the table rows before we start with rendering
        self.updateAfterActionExecution()

        #look for releases with 0 files
        bad = []
        for rel in self.context.values():
            if len(rel) == 0:
                bad.append(rel)

        if bad:
            self.status = _('WARNING: The following releases have NO files:')
            self.errors = [rel.__name__ for rel in bad]

            msg = _('WARNING: The following releases have NO files: $rels',
                    mapping={'rels': ', '.join(self.errors)})
            mypypi.api.logMirrorError(msg, self.context.pypiURL)
