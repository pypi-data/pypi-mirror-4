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
$Id: adding.py 1149 2008-05-11 03:17:29Z roger.ineichen $
"""

from z3c.menu.ready2go import item


# IUserManagementPage
class UserAddMenuItem(item.AddMenuItem):
    """User add menu item."""

    viewName = 'addUser.html'
    selected = False
    weight = 1


class GroupAddMenuItem(item.AddMenuItem):
    """Group add menu item."""

    viewName = 'addPYPIGroup.html'
    selected = False
    weight = 1


# IPYPISite
class LocalPackageAddMenuItem(item.AddMenuItem):
    """Local package add menu item."""

    viewName = 'addLocalPackage.html'
    selected = False
    weight = 1


class MirrorPackageAddMenuItem(item.AddMenuItem):
    """Mirror package add menu item."""

    viewName = 'addMirrorPackage.html'
    selected = False
    weight = 2


class MirrorPackageCollectionAddMenuItem(item.AddMenuItem):
    """Mirror package collection add menu item."""

    viewName = 'addMirrorPackageCollection.html'
    selected = False
    weight = 3


class CronSchedulerAddMenuItem(item.AddMenuItem):
    """Cron scheduler add menu item."""

    viewName = 'addCronScheduler.html'
    selected = False
    weight = 4


# ILocalPackage
class LocalReleaseAddMenuItem(item.AddMenuItem):
    """Local release add menu item."""

    viewName = 'addLocalRelease.html'
    selected = False
    weight = 1


# IMirrorPackage
class MirrorReleaseAddMenuItem(item.AddMenuItem):
    """Mirror release add menu item."""

    viewName = 'addMirrorRelease.html'
    selected = False
    weight = 1


# ILocalRelease
class ReleaseFileAddMenuItem(item.AddMenuItem):
    """Release files add menu item."""

    viewName = 'addReleaseFile.html'
    selected = False
    weight = 1

# IMirrorRelease
class MirrorReleaseFileAddMenuItem(item.AddMenuItem):
    """Release files add menu item."""

    viewName = 'addReleaseFile.html'
    selected = False
    weight = 1

    @property
    def available(self):
        """Available checker call"""
        return (len(self.context) == 0)

# IProject
class ProjectAddMenuItem(item.AddMenuItem):
    """IProject add menu item."""

    viewName = 'addProject.html'
    selected = False
    weight = 1

# IProjectFile
class ProjectFileAddMenuItem(item.AddMenuItem):
    """IProject file add menu item."""

    viewName = 'addProjectFile.html'
    selected = False
    weight = 1

# IProjectBuildoutFile
class ProjectBuildoutFileAddMenuItem(item.AddMenuItem):
    """IProject buildout file add menu item."""

    viewName = 'addProjectBuildoutFile.html'
    selected = False
    weight = 2

# IPublic
class PublicAddMenuItem(item.AddMenuItem):
    """IPublic add menu item."""

    viewName = 'addPublic.html'
    selected = False
    weight = 1

# IPublicFile
class PublicFileAddMenuItem(item.AddMenuItem):
    """IPublic file add menu item."""

    viewName = 'addPublicFile.html'
    selected = False
    weight = 1