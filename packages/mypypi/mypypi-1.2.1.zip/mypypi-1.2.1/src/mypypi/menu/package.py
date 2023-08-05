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
$Id: context.py 420 2007-04-08 13:49:39Z roger.ineichen $
"""

from z3c.menu.ready2go import item
from mypypi import interfaces


class ReleasesMenuItem(item.ContextMenuItem):
    """Releases menu."""

    contextInterface = interfaces.IPackage
    viewName = 'releases.html'
    weight = 1


class RolesMenuItem(item.ContextMenuItem):
    """Role grant menu."""

    contextInterface = interfaces.IPackage
    viewName = 'roles.html'
    weight = 2


class EditMenuItem(item.ContextMenuItem):
    """Pacakge edit menu."""

    contextInterface = interfaces.IPackage
    viewName = 'edit.html'
    weight = 3
