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


import zope.interface
import zope.component
from zope.securitypolicy.interfaces import IPrincipalRoleMap
from zope.securitypolicy.interfaces import IPrincipalRoleManager

from zope.authentication.interfaces import IAuthentication
from zope.authentication.interfaces import IEveryoneGroup

import z3c.tabular.table
from z3c.form import button
from z3c.table import column

from mypypi.i18n import MessageFactory as _
from mypypi import interfaces
from mypypi import authentication

ROLE_NAMES = ['mypypi.Administrator', 'mypypi.Member', 'mypypi.Owner']


class IHeadline(zope.interface.Interface):
    """Headline marker item."""

class IGroupHeadline(IHeadline):
    """Group headline marker item."""

class IUserHeadline(IHeadline):
    """User headline marker item."""


class GroupHeadline(object):
    """Group row."""

    zope.interface.implements(IGroupHeadline)

    __name__ = None

    def __init__(self, request):
        self.request = request

    @property
    def title(self):
        return zope.i18n.translate(_('<strong>Groups</strong>'),
            context=self.request)


class UserHeadline(object):
    """User row."""

    zope.interface.implements(IUserHeadline)

    __name__ = None

    def __init__(self, request):
        self.request = request

    @property
    def title(self):
        return zope.i18n.translate(_('<strong>Users</strong>'),
            context=self.request)


class GroupTitleColumn(column.Column):
    """Group name column."""

    header = _('Groups & Users/Roles')

    def renderCell(self, item):
        """Setup link content."""
        if interfaces.IPYPIUser.providedBy(item):
            return '%s, %s (%s)' % (item.firstName, item.lastName, item.login)
        return item.title


class AdministratorRoleColumn(column.Column):
    """Administrator role column."""

    header = _('Administrator')

    def renderCell(self, item):
        if IHeadline.providedBy(item):
            return u''
        prMap = IPrincipalRoleMap(self.context)
        rid = 'mypypi.Administrator'
        pidsForRole = [grp[0] for grp in prMap.getPrincipalsForRole(rid)]
        selected=''
        idStr = '%s.%s' % (rid, item.__name__)
        if item.__name__ in pidsForRole:
            selected=' checked="checked"'
        disabled = u''
        if interfaces.IPYPIAdmin.providedBy(item) or \
            item.__name__ == 'groups.Administrators':
            selected=' checked="checked"'
            disabled = ' disabled="disabled"'
        widget = u'<input type="checkbox" class="checkbox-widget" '
        widget += u'name="%s" value="on"%s%s/>'
        return widget %(idStr, selected, disabled)


class OwnerRoleColumn(column.Column):
    """Owner role column."""

    header = _('Owner')

    def renderCell(self, item):
        if IHeadline.providedBy(item):
            return u''
        prMap = IPrincipalRoleMap(self.context)
        rid = 'mypypi.Owner'
        pidsForRole = [grp[0] for grp in prMap.getPrincipalsForRole(rid)]
        selected=''
        idStr = '%s.%s' % (rid, item.__name__)
        if item.__name__ in pidsForRole:
            selected=' checked="checked"'
        disabled = u''
        if interfaces.IPYPIAdmin.providedBy(item) or \
            item.__name__ == 'groups.Owners':
            selected=' checked="checked"'
            disabled = ' disabled="disabled"'
        widget = u'<input type="checkbox" class="checkbox-widget" '
        widget += u'name="%s" value="on"%s%s/>'
        return widget %(idStr, selected, disabled)


class MemberRoleColumn(column.Column):
    """Member role column."""

    header = _('Member')

    def renderCell(self, item):
        if IHeadline.providedBy(item):
            return u''
        prMap = IPrincipalRoleMap(self.context)
        rid = 'mypypi.Member'
        pidsForRole = [grp[0] for grp in prMap.getPrincipalsForRole(rid)]
        selected=''
        idStr = '%s.%s' % (rid, item.__name__)
        if item.__name__ in pidsForRole:
            selected=' checked="checked"'
        disabled = u''
        if interfaces.IPYPIAdmin.providedBy(item) or \
            item.__name__ == 'groups.Members':
            selected=' checked="checked"'
            disabled = ' disabled="disabled"'
        widget = u'<input type="checkbox" class="checkbox-widget" '
        widget += u'name="%s" value="on"%s%s/>'
        return widget %(idStr, selected, disabled)


class RoleManagementBase(z3c.tabular.table.FormTable):
    """Role management page."""

    zope.interface.implements(interfaces.IReleaseManagementPage)

    buttons = z3c.tabular.table.FormTable.buttons.copy()
    handlers = z3c.tabular.table.FormTable.handlers.copy()

    label = _('Role Management')

    formErrorsMessage = _('There were some errors.')
    updateNoItemsMessage = _('No items selected for update')
    ignoreContext = True
    errors  = []
    _auth = None

    batchSize = 100
    startBatchingAt = 100

    def setUpColumns(self):
        return [
            column.addColumn(self, GroupTitleColumn, u'title',
                             weight=1),
            column.addColumn(self, AdministratorRoleColumn, u'administrator',
                             weight=2),
            column.addColumn(self, OwnerRoleColumn, u'owner',
                             weight=4),
            column.addColumn(self, MemberRoleColumn, u'member',
                             weight=4),
            ]

    @property
    def auth(self):
        if self._auth is None:
            self._auth = zope.component.getUtility(IAuthentication)
        return self._auth

    def sortRows(self):
        pass

    @property
    def values(self):
        res = []
        append = res.append
        append(GroupHeadline(self.request))
        groups = [grp for __name__, grp in self.auth['groups'].items()]
        groups = sorted(groups, key=lambda item: item.__name__.lower())
        res += groups
        append(UserHeadline(self.request))
        principals = [prin for __name__, prin in self.auth['users'].items()]
        principals = sorted(principals, key=lambda item: item.lastName.lower())
        res += principals
        return res

    @button.buttonAndHandler(u'Save Roles', name='saveRoles')
    def handleSaveRoles(self, action):
        prMap = IPrincipalRoleMap(self.context)
        prm = IPrincipalRoleManager(self.context)
        pids = []
        append = pids.append
        for __name__, grp in self.auth['groups'].items():
            append(__name__)
        for __name__, principal in self.auth['users'].items():
            # skip changes for IPYPIAdmin
            if not interfaces.IPYPIAdmin.providedBy(principal):
                append(__name__)

        changed = False

        for rid in ROLE_NAMES:
            pidsForRole = [grp[0] for grp in prMap.getPrincipalsForRole(rid)]
            for pid in pids:
                idStr = '%s.%s' %(rid, pid)
                if idStr in self.request:
                    # add role
                    if pid not in pidsForRole:
                        prm.assignRoleToPrincipal(rid, pid)
                        print "assign rid: %s, pid: %s" % (rid, pid)
                        changed = True
                else:
                    # remove role but not for our internal ones
                    if pid in pidsForRole:
                        
                        # skip remove default roles from defualt groups
                        if pid == 'groups.Administrators' and \
                            rid == 'mypypi.Administrator':
                            continue
                        if pid == 'groups.Members' and rid == 'mypypi.Member':
                            continue
                        if pid == 'groups.Owners' and rid == 'mypypi.Owner':
                            continue

                        prm.unsetRoleForPrincipal(rid, pid)
                        print "remove rid: %s, pid: %s" % (rid, pid)
                        changed = True
        if changed is True:
            self.status = _('Roles have been successfully changed.')


class SiteRoles(RoleManagementBase):
    """Site roles management."""


class PackageRoles(RoleManagementBase):
    """Package roles management."""
