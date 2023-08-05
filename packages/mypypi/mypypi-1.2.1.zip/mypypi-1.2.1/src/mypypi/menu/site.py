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
$Id: virtualsite.py 334 2007-03-15 01:38:06Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

from zope.traversing.browser import absoluteURL
from zope.component import hooks

from z3c.menu.ready2go import item

from mypypi import interfaces


# generic context menu items
class PackagesMenuItem(item.ContextMenuItem):
    """Packages menu item."""

    viewName = 'packages.html'
    contextInterface = interfaces.IPYPISite
    weight = 10


class ProjectsMenuItem(item.ContextMenuItem):
    """Projects menu item."""

    viewName = '++projects++/index.html'
    contextInterface = interfaces.IPYPISite
    weight = 20


class PublicMenuItem(item.ContextMenuItem):
    """Public menu item."""

    viewName = '++public++/index.html'
    contextInterface = interfaces.IPYPISite
    weight = 20


class HistoryMenuItem(item.ContextMenuItem):
    """History menu item."""

    viewName = 'history.html'
    contextInterface = interfaces.IPYPISite
    weight = 30


class UsersMenuItem(item.ContextMenuItem):
    """Users menu."""

    viewName = 'users.html'
    contextInterface = interfaces.IPYPISite
    weight = 40

    def url(self):
        site = hooks.getSite()
        baseURL = absoluteURL(site, self.request)
        return baseURL + '/' + self.viewName


class GroupsMenuItem(item.ContextMenuItem):
    """Groups menu."""

    viewName = 'groups.html'
    contextInterface = interfaces.IPYPISite
    weight = 50

    def url(self):
        site = hooks.getSite()
        baseURL = absoluteURL(site, self.request)
        return baseURL + '/' + self.viewName


class RolesMenuItem(item.ContextMenuItem):
    """Roles menu."""

    viewName = 'roles.html'
    contextInterface = interfaces.IPYPISite
    weight = 60

    def url(self):
        site = hooks.getSite()
        baseURL = absoluteURL(site, self.request)
        return baseURL + '/' + self.viewName


class ProcessorMenuItem(item.ContextMenuItem):
    """Remote Processor menu."""

    viewName = 'processor.html'
    contextInterface = interfaces.IPYPISite
    weight = 70


class JobsMenuItem(item.ContextMenuItem):
    """Jobs menu."""

    viewName = 'jobs.html'
    contextInterface = interfaces.IPYPISite
    weight = 80


class SchedulerMenuItem(item.ContextMenuItem):
    """Scheduler items menu."""

    viewName = 'scheduler.html'
    contextInterface = interfaces.IPYPISite
    weight = 90


class EditMenuItem(item.ContextMenuItem):
    """Site edit menu."""

    viewName = 'edit.html'
    contextInterface = interfaces.IPYPISite
    weight = 100


# server control
class ErrorsMenuItem(item.ContextMenuItem):
    """Errors menu."""

    viewName = 'errors.html'
    weight = 1


class ErrorEditMenuItem(item.ContextMenuItem):
    """Error edit menu."""

    viewName = 'editError.html'
    weight = 2


class RuntimeMenuItem(item.ContextMenuItem):
    """Runtime menu item."""

    viewName = 'runtime.html'
    weight = 3


class ZODBControlMenuItem(item.ContextMenuItem):
    """ZODB control menu item."""

    viewName = 'ZODBControl.html'
    weight = 4


class GenerationsMenuItem(item.ContextMenuItem):
    """Generation management menu item."""

    viewName = 'generations.html'
    weight = 5
