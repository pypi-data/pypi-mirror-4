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


class UserAddForm(form.AddForm):

    template = getPageTemplate(name='simple')

    buttons = form.AddForm.buttons.copy()
    handlers = form.AddForm.handlers.copy()

    prefix = 'user'
    label = _('Add User')

    fields = field.Fields(interfaces.IPYPIUser).select(
        'login', 'password', 'title', 'description', 'firstName', 'lastName',
        'email', 'phone')

    def createAndAdd(self, data):
        # Create the admin principal
        login = data['login']
        password = data['password']
        description = data['description']
        title = data['title']
        obj = authentication.PYPIUser(login, password, title, description)
        obj.firstName = data.get('firstName', u'')
        obj.lastName = data.get('lastName', u'')
        obj.email = data.get('email', u'')
        obj.phone = data.get('phone', u'')
        
        # notify
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))

        # add the user
        auth = zope.component.getUtility(IAuthentication, context=self.context)
        auth['users'].add(obj)

        # configure
        configurator.configure(obj, data)

        self._finishedAdd = True
        return obj

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.getURL())

    def nextURL(self):
        return '%s/users.html' % absoluteURL(self.context, self.request)


class UserEditForm(form.EditForm):

    template = getPageTemplate(name='subform')

    buttons = form.EditForm.buttons.copy()
    handlers = form.EditForm.handlers.copy()
    ignoreRequest = False

    label = _('Edit User')
    prefix = 'userform'

    fields = field.Fields(interfaces.IPYPIUser).select(
        'login', 'password', 'title', 'description', 'firstName', 'lastName',
        'email', 'phone')

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.getURL())


# user management helpers
class UserNameColumn(column.SelectedItemColumn):
    """User name column."""

    def getLinkContent(self, item):
        """Setup link content."""
        return u'%s, %s (%s)' %(item.lastName, item.firstName, item.login)


class GroupColumn(column.Column):

    group = None

    def renderCell(self, item):
        widget = u'<input type="checkbox" class="checkbox-widget" '
        widget += u'name="%s.%s" value="on" %s />'
        selected=''
        pid = item.__name__
        if pid in self.group.principals:
            selected='checked="checked"'
        return widget %(self.group.__name__, pid, selected)


class Users(z3c.tabular.table.SubFormTable):
    """User management table."""

    zope.interface.implements(interfaces.IUserManagementPage)

    buttons = z3c.tabular.table.SubFormTable.buttons.copy()
    handlers = z3c.tabular.table.SubFormTable.handlers.copy()

    label = _('User Management and Group settings')
    deleteSucsessMessage = _('User has been deleted.')
    msgCanNotRemoveAdminGroup = _(
        "Can't remove the default Administrator from the Administrators group")
    msgCanNotRemoveAdmin = _(
        "Can't remove the default Administrator")
    _auth = None

    subFormClass = UserEditForm

    def setUpColumns(self):
        groups = sorted(self.groups, key=lambda g: g.title)
        columns = [
            column.addColumn(self, column.RadioColumn, u'radio',
                             weight=1),
            column.addColumn(self, UserNameColumn, u'userName',
                             weight=2),
            ]
        weight = 3
        groups = sorted(self.groups, key=lambda g: g.title)
        for group in groups:
            if group.__name__ != 'groups.Everyone':
                columns.append(column.addColumn(self,
                    GroupColumn, group.__name__, header=group.title,
                    weight=weight, group=group))
            weight += 1
        return columns

    @property
    def auth(self):
        if self._auth is None:
            self._auth = zope.component.getUtility(IAuthentication)
        return self._auth

    @property
    def values(self):
        for user in self.auth['users'].values():
            yield user

    @property
    def groups(self):
        for name, grp in self.auth['groups'].items():
            yield grp

    @button.buttonAndHandler(u'Save Groups', name='saveGroups')
    def handleSaveGroups(self, action):
        groups = self.auth['groups']
        users = self.auth['users']
        changed = False
        for pid, user in users.items():
            gids = groups.getGroupsForPrincipal(pid)
            for gid in [g.__name__ for g in groups.values()]:
                grp = groups.queryPrincipal(gid)
                idStr = '%s.%s' %(gid, pid)
                if idStr in self.request:
                    if gid not in gids:
                        grp.principals += (pid,)
                        changed = True
                else:
                    if gid in gids:
                        
                        if interfaces.IPYPIAdmin.providedBy(user) and \
                            gid == 'groups.Administrators':
                            self.status = self.msgCanNotRemoveAdminGroup
                            continue
                        principals = list(grp.principals)
                        principals.remove(pid)
                        grp.principals = tuple(principals)
                        changed = True
        if changed is True:
            self.status = _('Groups have been successfully changed.')

    def executeDelete(self, item):
        """Do the actual item deletion."""
        pid = item.__name__
        principal = self.auth['users'][pid]
        if interfaces.IPYPIAdmin.providedBy(principal):
            self.status = self.msgCanNotRemoveAdmin
            transaction.doom()
            return
        del self.auth['users'][pid]

        # cleanup group settings for removed users
        for group in self.auth['groups'].values():
            if pid in group.principals:
                principals = list(group.principals)
                principals.remove(pid)
                group.setPrincipals(principals, check=False)
