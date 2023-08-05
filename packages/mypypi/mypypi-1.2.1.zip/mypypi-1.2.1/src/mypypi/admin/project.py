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
$Id: project.py 2990 2012-07-01 22:23:20Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.event
import zope.lifecycleevent
import zope.security
from zope.traversing.browser import absoluteURL

import z3c.tabular.table
from z3c.template.template import getPageTemplate
from z3c.template.template import getLayoutTemplate
from z3c.configurator import configurator
from z3c.form import field
from z3c.form import button
from z3c.formui import form
from z3c.table import column

from mypypi.i18n import MessageFactory as _
from mypypi import interfaces
from mypypi import project


class ProjectAddForm(form.AddForm):

    template = getPageTemplate(name='simple')

    buttons = form.AddForm.buttons.copy()
    handlers = form.AddForm.handlers.copy()

    label = _('Add Project')

    fields = field.Fields(interfaces.IProject).select('__name__',
        'title')

    def createAndAdd(self, data):
        __name__ = data['__name__']
        __name__ = __name__.replace(' ', '')
        title = data['title']
        obj = project.Project(title)
        self.contentName = __name__
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))

        self.context[self.contentName] = obj

        #configure
        configurator.configure(obj, data)
        return obj

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.getURL())

    def nextURL(self):
        return '%s/index.html' % absoluteURL(self.context, self.request)


class ProjectEditForm(form.EditForm):

    template = getPageTemplate(name='subform')

    buttons = form.EditForm.buttons.copy()
    handlers = form.EditForm.handlers.copy()
    ignoreRequest = False

    label = _('Edit Project')
    prefix = 'groupform'

    fields = field.Fields(interfaces.IProject).select('title')

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.getURL())


class ProjectNameColumn(column.LinkColumn):
    """Project name column."""

    header = _('Name')
    linkName = 'files.html'

    #def renderCell(self, item):
    #    """Setup link content."""
    #    return item.__name__

    def getLinkContent(self, item):
        """Setup link content."""
        return item.__name__

class ProjectTitleColumn(column.LinkColumn):
    """Project title column."""

    header = _('Title')
    linkName = 'files.html'

    #def renderCell(self, item):
    #    """Setup link content."""
    #    return item.title

    def getLinkContent(self, item):
        """Setup link content."""
        return item.title


class Projects(z3c.tabular.table.SubFormTable):
    """Projects management table."""

    zope.interface.implements(interfaces.IProjectManagementPage)

    buttons = z3c.tabular.table.SubFormTable.buttons.copy()
    handlers = z3c.tabular.table.SubFormTable.handlers.copy()

    label = _('Project Management')
    deleteSucsessMessage = _('Project has been deleted.')

    batchSize = 100
    startBatchingAt = 100

    subFormClass = ProjectEditForm

    def setUpColumns(self):
        return [
            column.addColumn(self, column.RadioColumn, u'radio',
                             weight=1, cssClasses={'th':'firstColumnHeader'}),
            column.addColumn(self, ProjectNameColumn, u'name',
                             weight=2),
            column.addColumn(self, ProjectTitleColumn, u'title',
                             weight=3),
            ]

    def setupConditions(self):
        interaction = zope.security.management.getInteraction()
        self.allowDelete = interaction.checkPermission('mypypi.ManageProjects',
                                           self.context)
        self.allowEdit = self.allowDelete

        super(Projects, self).setupConditions()

    @property
    def values(self):
        return self.context.values()

    def executeDelete(self, item):
        """Do the actual deletion."""
        del self.context[item.__name__]
