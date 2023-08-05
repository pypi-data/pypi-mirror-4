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
$Id: user.py 1449 2008-07-05 13:43:11Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import transaction

import zope.interface
import zope.component
import zope.event
import zope.lifecycleevent
from zope.traversing.browser import absoluteURL

from zope.authentication.interfaces import IAuthentication

import z3c.tabular.table
from z3c.template.template import getPageTemplate
from z3c.configurator import configurator
from z3c.form import field
from z3c.form import button
from z3c.formui import form
from z3c.table import column

from mypypi.i18n import MessageFactory as _
from mypypi import interfaces
from mypypi import authentication

HIDDEN_GROUP_NAMES = ['groups.Administrators', 'groups.Owners',
    'groups.Members']


class GroupAddForm(form.AddForm):

    template = getPageTemplate(name='simple')

    buttons = form.AddForm.buttons.copy()
    handlers = form.AddForm.handlers.copy()

    label = _('Add Group')
    _auth = None

    fields = field.Fields(interfaces.IPYPIGroup).select('__name__',
        'title', 'description')

    def createAndAdd(self, data):
        __name__ = data['__name__']
        __name__ = __name__.replace(' ', '')
        title = data['title']
        description = data['description']
        obj = authentication.PYPIGroup(title, description)
        prefix = self._groups.prefix
        if not __name__.startswith(prefix):
            __name__ = prefix + __name__
        self.contentName = __name__
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
        self._groups[self.contentName] = obj

        #configure
        configurator.configure(obj, data)
        return obj

    @property
    def _groups(self):
        if self._auth is None:
            self._auth = zope.component.getUtility(IAuthentication)
        return self._auth['groups']

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.getURL())

    def nextURL(self):
        return '%s/groups.html' % absoluteURL(self.context, self.request)


class GroupEditForm(form.EditForm):

    template = getPageTemplate(name='subform')

    buttons = form.EditForm.buttons.copy()
    handlers = form.EditForm.handlers.copy()
    ignoreRequest = False

    label = _('Edit Group')
    prefix = 'groupform'

    fields = field.Fields(interfaces.IPYPIGroup).select(
        'title', 'description')

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.getURL())


class GroupTitleColumn(column.Column):
    """Group title column."""

    header = _('Title')

    def renderCell(self, item):
        """Setup link content."""
        return item.title


class GroupDescriptionColumn(column.Column):
    """Group description column."""

    header = _('Description')

    def renderCell(self, item):
        """Setup link content."""
        return item.description


class Groups(z3c.tabular.table.SubFormTable):
    """Group management table."""

    zope.interface.implements(interfaces.IGroupManagementPage)

    buttons = z3c.tabular.table.SubFormTable.buttons.copy()
    handlers = z3c.tabular.table.SubFormTable.handlers.copy()

    label = _('Group Management')
    deleteSucsessMessage = _('Group has been deleted.')
    _auth = None

    batchSize = 100
    startBatchingAt = 100

    subFormClass = GroupEditForm

    def setUpColumns(self):
        return [
            column.addColumn(self, column.RadioColumn, u'radio',
                             weight=1, cssClasses={'th':'firstColumnHeader'}),
            column.addColumn(self, GroupTitleColumn, u'title',
                             weight=2),
            column.addColumn(self, GroupDescriptionColumn, u'description',
                             weight=2),
            ]

    @property
    def auth(self):
        if self._auth is None:
            self._auth = zope.component.getUtility(IAuthentication)
        return self._auth

    @property
    def values(self):
        return self.auth['groups'].values()

    def executeDelete(self, item):
        """Do the actual group deletion."""
        if item.__name__ in HIDDEN_GROUP_NAMES:
            self.status = _('The group $name is not removable.', mapping={
                'name':item.__name__})
            transaction.doom()
            return
        del self.auth['groups'][item.__name__]
