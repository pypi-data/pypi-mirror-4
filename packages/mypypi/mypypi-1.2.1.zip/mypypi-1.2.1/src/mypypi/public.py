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
$Id: public.py 2989 2012-07-01 22:04:20Z roger.ineichen $
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
from mypypi.interfaces import PUBLIC_CONTAINER_KEY
from mypypi.interfaces import LOGGER_KEY


class PublicContainer(btree.BTreeContainer):
    """Public container."""

    zope.interface.implements(interfaces.IPublicContainer)

    def __repr__(self):
        return "<%s %r>" %(self.__class__.__name__, self.__name__)


class Public(btree.BTreeContainer):
    """Public."""

    zope.interface.implements(interfaces.IPublic)

    title = FieldProperty(interfaces.IPublic['title'])

    def __init__(self, title):
        super(Public, self).__init__()
        self.title = title


class PublicFile(FSFile):
    """Release file system file."""

    zope.interface.implements(interfaces.IPublicFile)

    size = FieldProperty(interfaces.IPublicFile['size'])


@zope.component.adapter(interfaces.IPYPISite)
@zope.interface.implementer(interfaces.IPublicContainer)
def getPublicContainer(context):
    annotations = IAnnotations(context)
    try:
        return annotations[PUBLIC_CONTAINER_KEY]
    except KeyError:
        obj = PublicContainer()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
        annotations[PUBLIC_CONTAINER_KEY] = obj
        name = '++public++'
        zope.location.locate(annotations[PUBLIC_CONTAINER_KEY], context, name)
        return annotations[PUBLIC_CONTAINER_KEY]
# Help out apidoc
getPublicContainer.factory = PublicContainer


class publicNamespace(object):

    def __init__(self, ob, request=None):
        self.context = ob

    def traverse(self, name, ignore):
        return interfaces.IPublicContainer(self.context)