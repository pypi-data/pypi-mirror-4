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
$Id: project.py 3362 2012-11-18 01:37:52Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import re

import zope.interface
import zope.component
import zope.event
import zope.lifecycleevent
import zope.schema
import zope.security
from zope.traversing.browser import absoluteURL
from zope.publisher.browser import BrowserPage
from zope.exceptions.interfaces import DuplicationError

import z3c.tabular.table
from z3c.template.template import getPageTemplate
from z3c.template.template import getLayoutTemplate
from z3c.form import field
from z3c.form import button
from z3c.formui import form
from z3c.table import column

import p01.fsfile.schema
import p01.fsfile.browser
import p01.fsfile.interfaces
import p01.tmp.interfaces

from mypypi.i18n import MessageFactory as _
from mypypi import interfaces
from mypypi import project
from mypypi.browser.setuptools import errorResponse


class EditLinkColumn(column.EditLinkColumn):

    header = _(u'Edit')
    linkContent = _(u'Edit')

    def renderCell(self, item):
        if interfaces.IProjectFileBuildout.providedBy(item):
            return super(EditLinkColumn, self).renderCell(item)
        else:
            return u''


class ProjectFiles(z3c.tabular.table.DeleteFormTable):
    """Project file management page."""

    zope.interface.implements(interfaces.IProjectFileManagementPage)

    buttons = z3c.tabular.table.DeleteFormTable.buttons.copy()
    handlers = z3c.tabular.table.DeleteFormTable.handlers.copy()

    formErrorsMessage = _('There were some errors.')
    ignoreContext = True
    errors  = []

    batchSize = 500
    startBatchingAt = 500

    simpleLayout = getLayoutTemplate('simple')
    simpleTemplate = getPageTemplate(name='simple')

    def __init__(self, context, request):
        if request.get('HTTP_USER_AGENT', '').lower().startswith('python-'):
            self.layout = self.simpleLayout
            self.template = self.simpleTemplate

        super(ProjectFiles, self).__init__(context, request)

    def setUpColumns(self):
        return [
            column.addColumn(self, column.CheckBoxColumn, u'checkbox',
                             weight=1, cssClasses={'th':'firstColumnHeader'}),
            column.addColumn(self, EditLinkColumn, u'edit',
                             weight=2),
            column.addColumn(self, column.LinkColumn, u'__name__',
                             weight=3),
            column.addColumn(self, column.CreatedColumn, name=u'created',
                             weight=4, header=u'Created'),
            column.addColumn(self, column.ModifiedColumn, name=u'modified',
                             weight=5, header=u'Modified')
            ]

    def setupConditions(self):
        interaction = zope.security.management.getInteraction()
        self.allowDelete = interaction.checkPermission('mypypi.ManageProjects',
                                           self.context)
        super(ProjectFiles, self).setupConditions()

    @property
    def label(self):
        return _('Project File Management for $projectName',
            mapping={'projectName': self.context.__name__})

    def executeDelete(self, item):
        del self.context[item.__name__]

    def getCreatedDate(self, item):
        dc = IZopeDublinCore(item, None)
        v = dc.created
        if v is not None:
            return v.isoformat()
        return ''

    @property
    def links(self):
        baseURL = absoluteURL(self.context, self.request)
        return [{'name':name,
                  'url': '%s/%s' % (baseURL, name),
                  #'date': self.getCreatedDate(fle),
                  }
                for name, fle in self.context.items()]


class IProjectFileUploadSchema(interfaces.IProjectFile):
    """Project file upload schema."""

    upload = p01.fsfile.schema.FSFileUpload(
        title=_(u'Project File'),
        description=_('The release file distribution.'),
        fsStorageName=u'',
        fsNameSpace=u'upload', # use upload storage
        fsFileFactory=project.ProjectFile,
        allowEmptyPostfix=False,
        required=True)


class ProjectFileAddForm(form.AddForm):

    template = getPageTemplate(name='simple')

    buttons = form.AddForm.buttons.copy()
    handlers = form.AddForm.handlers.copy()

    label = _('Add Project File')

    fields = field.Fields(IProjectFileUploadSchema).select('__name__',
        'upload', 'commentText')

    def createAndAdd(self, data):
        try:
            # create
            name = data['__name__']
            projectFile = data['upload']

            # notify
            zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(
                projectFile))

            # add the release file
            self.context[name] = projectFile

            self._finishedAdd = True
            return projectFile

        except (KeyError, DuplicationError), e:
            self.status = _('Project file with the same name already exists.')
            return

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.getURL())

    def nextURL(self):
        return '%s/files.html' % absoluteURL(self.context, self.request)


class IProjectFileBuildoutUploadSchema(interfaces.IProjectFile):
    """Project file upload schema."""

    upload = p01.fsfile.schema.FSFileUpload(
        title=_(u'Project File'),
        description=_('The release file distribution.'),
        fsStorageName=u'',
        fsNameSpace=u'upload', # use upload storage
        fsFileFactory=project.ProjectFileBuildout,
        allowEmptyPostfix=False,
        required=True)

class ProjectFileBuildoutAddForm(ProjectFileAddForm):

    #template = getPageTemplate(name='simple')

    buttons = ProjectFileAddForm.buttons.copy()
    handlers = ProjectFileAddForm.handlers.copy()

    label = _('Add Project Buildout File')

    fields = field.Fields(IProjectFileBuildoutUploadSchema).select('__name__',
        'upload', 'commentText')

    def createAndAdd(self, data):
        try:
            # create
            name = data['__name__'].strip()
            if not name.lower().endswith('.cfg'):
                name += '.cfg'

            projectFile = data['upload']

            # notify
            zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(
                projectFile))

            # add the release file
            self.context[name] = projectFile

            self._finishedAdd = True
            return projectFile

        except DuplicationError, e:
            self.status = _('Project file with the same name already exists.')
            return
    #
    #@button.buttonAndHandler(u'Cancel')
    #def handleCancel(self, action):
    #    self.request.response.redirect(self.request.getURL())
    #
    #def nextURL(self):
    #    return '%s/files.html' % absoluteURL(self.context, self.request)

    @button.buttonAndHandler(_(u'Add blank file'))
    def handleAddBlank(self, action):
        data, errors = self.extractData()

        if not data.get('__name__') and errors:
            self.status = self.formErrorsMessage
            return

        #TODO

def newFile(factory, filename, content=None, tmpFile=None):
    # get storage based on fields fsStorageName value
    fsStorage = zope.component.getUtility(p01.fsfile.interfaces.IFSStorage, '')
    tmpStorage = zope.component.getUtility(p01.tmp.interfaces.ITMPStorage)
    if tmpFile is None:
        tmpStorage = zope.component.getUtility(p01.tmp.interfaces.ITMPStorage)
        tmpFile = tmpStorage.getTMPFile()
        if isinstance(content, unicode):
            content = content.encode('utf-8')
        tmpFile.write(content)
        tmpFile.close()
    return fsStorage.store(tmpFile, filename, u'upload', factory)

class ProjectFileDownload(p01.fsfile.browser.FSFileDownload):
    """Project file download."""

    def __call__(self):
        return super(ProjectFileDownload, self).__call__()

class ProjectFileEditForm(form.EditForm):

    template = getPageTemplate(name='simple')

    label = _('Edit Project File')

    fields = field.Fields(interfaces.IProjectFile).select('published')

class IProjectFileBuildoutEditSchema(interfaces.IProjectFileBuildout):

    content = zope.schema.SourceText(
        title = _(u'Content'),
        description = _(u'File content'),
        default=u'',
        required=False)

VERSION = re.compile(r'-(\d+\.\d+(\.\d+){0,2})')


class ProjectFileBuildoutEditForm(form.EditForm):

    template = getPageTemplate(name='simple')

    label = _('Edit Project Buildout File')

    fields = field.Fields(IProjectFileBuildoutEditSchema).select(
        'content', 'published')

    def getContent(self):
        reader = p01.fsfile.interfaces.IFSFileReader(self.context)
        content = reader.read()

        return dict(content=content, published=self.context.published)

    def nextURL(self):
        return '%s/files.html' % absoluteURL(self.context.__parent__,
                                             self.request)

    def saveIt(self, name, delete=True):
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage
            return

        newfile = newFile(project.ProjectFileBuildout, name, content=data['content'])

        container = self.context.__parent__
        if delete:
            del container[self.context.__name__]
        container[name] = newfile

        self.context = newfile

        self.status = _(u'Saved')

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_(u'Save'))
    def handleSave(self, action):
        name = self.context.__name__
        self.saveIt(name, delete=True)
        #self.request.response.redirect(self.nextURL())

    @button.buttonAndHandler(_(u'Save as new version'),
                             condition=lambda form: VERSION.search(form.context.__name__))
    def handleSaveNewVersion(self, action):
        m = VERSION.search(self.context.__name__)
        version = m.group(1)
        parts = version.split('.')
        parts[-1] = str(int(parts[-1])+1)
        version = '.'.join(parts)

        newName = VERSION.sub('-'+version, self.context.__name__)

        self.saveIt(newName, delete=False)

        self.request.response.redirect(self.nextURL())


class FileUploadPage(BrowserPage):
    """``upload`` page used by keas.build"""

    def __call__(self):
        """Receive release package upload.

        The given form data is a dict which contains the following content:

        {u'content': <zope.publisher.browser.FileUpload object at 0x02944BF0>,
         }

        """
        data = self.request.form

        try:
            fname = data['content'].filename.strip()
            if fname.endswith('.cfg'):
                factory = project.ProjectFileBuildout
            else:
                factory = project.ProjectFile
            newfile = newFile(factory, fname, tmpFile=data['content'].tmpFile)

            self.context[fname] = newfile
        except Exception, e:
            return errorResponse(self.request, repr(e))

        return 'OK'
