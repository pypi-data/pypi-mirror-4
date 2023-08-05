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
$Id: project.py 2205 2011-01-03 23:26:44Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
import zope.location
import zope.event
import zope.lifecycleevent
from zope.annotation.interfaces import IAnnotations
from zope.schema.fieldproperty import FieldProperty
from zope.container import btree

from p01.fsfile.file import FSFile

from mypypi import interfaces
from mypypi import release
from mypypi import layer
from mypypi.interfaces import PROJECT_CONTAINER_KEY
from mypypi.interfaces import LOGGER_KEY


class ProjectContainer(btree.BTreeContainer):
    """Project container."""

    zope.interface.implements(interfaces.IProjectContainer)

    def __repr__(self):
        return "<%s %r>" %(self.__class__.__name__, self.__name__)


class Project(btree.BTreeContainer):
    """Project."""

    zope.interface.implements(interfaces.IProject)

    title = FieldProperty(interfaces.IProject['title'])

    def __init__(self, title):
        super(Project, self).__init__()
        self.title = title

class ProjectFile(FSFile):
    """Release file system file."""

    zope.interface.implements(interfaces.IProjectFile)

    commentText = FieldProperty(interfaces.IProjectFile['commentText'])
    downloads = FieldProperty(interfaces.IProjectFile['downloads'])
    size = FieldProperty(interfaces.IProjectFile['size'])

    published = FieldProperty(interfaces.IProjectFile['published'])

    @property
    def isPublished(self):
        return self.published

class ProjectFileBuildout(ProjectFile):
    """Release file system file."""

    zope.interface.implements(interfaces.IProjectFileBuildout)


@zope.component.adapter(interfaces.IPYPISite)
@zope.interface.implementer(interfaces.IProjectContainer)
def getProjectContainer(context):
    annotations = IAnnotations(context)
    try:
        return annotations[PROJECT_CONTAINER_KEY]
    except KeyError:
        obj = ProjectContainer()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
        annotations[PROJECT_CONTAINER_KEY] = obj
        name = '++projects++'
        zope.location.locate(annotations[PROJECT_CONTAINER_KEY], context, name)
        return annotations[PROJECT_CONTAINER_KEY]
# Help out apidoc
getProjectContainer.factory = ProjectContainer

class projectsNamespace(object):

    def __init__(self, ob, request=None):
        self.context = ob

    def traverse(self, name, ignore):
        return interfaces.IProjectContainer(self.context)