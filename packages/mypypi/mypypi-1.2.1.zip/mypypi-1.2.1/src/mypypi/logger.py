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
$Id:$
"""
__docformat__ = "reStructuredText"

import persistent
import zope.interface
import zope.component
import zope.location
import zope.event
import zope.lifecycleevent
from zope.annotation.interfaces import IAnnotations
from zope.schema.fieldproperty import FieldProperty
from zope.security.management import getInteraction
from zope.authentication.interfaces import IAuthentication
from zope.component import hooks
from zope.container import contained
from zope.container import btree

from mypypi import interfaces
from mypypi import release
from mypypi import layer
from mypypi.interfaces import LOG_CONTAINER_KEY
from mypypi.interfaces import LOGGER_KEY


class LogContainer(btree.BTreeContainer):
    """Log container."""

    zope.interface.implements(interfaces.ILogContainer)

    def __init__(self):
        super(LogContainer, self).__init__()
        self.counter = 0

    def __setitem__(self, key, object):
        """Disabeld, use add method instead."""
        raise NotImplementedError('Use add method instead.')

    def add(self, logger):
        """Add a new logger."""
        self.counter += 1
        while unicode(self.counter) in self:
            self.counter += 1
        key = unicode(self.counter)
        super(LogContainer, self).__setitem__(key, logger)

    def __repr__(self):
        return "<%s %r>" %(self.__class__.__name__, self.__name__)


class HistoryEntry(persistent.Persistent, contained.Contained):
    """History entry."""

    zope.interface.implements(interfaces.IHistoryEntry)

    message = FieldProperty(interfaces.IHistoryEntry['message'])
    path = FieldProperty(interfaces.IHistoryEntry['path'])

    def __init__(self, message, path=None):
        super(HistoryEntry, self).__init__()
        self.message = message
        if path is not None:
            self.path = unicode(path)


class ErrorEntry(persistent.Persistent, contained.Contained):
    """Error entry."""

    zope.interface.implements(interfaces.IErrorEntry)

    message = FieldProperty(interfaces.IErrorEntry['message'])
    path = FieldProperty(interfaces.IErrorEntry['path'])

    def __init__(self, message, path=None):
        super(ErrorEntry, self).__init__()
        self.message = message
        if path is not None:
            self.path = unicode(path)


class Logger(btree.BTreeContainer):
    """Logger."""

    zope.interface.implements(interfaces.ILogger)
    zope.component.adapts(layer.IPYPICoreLayer)

    userName = FieldProperty(interfaces.ILogger['userName'])

    def __init__(self):
        super(Logger, self).__init__()
        self.counter = 0

    def __setitem__(self, key, object):
        """Disabeld, use add method instead."""
        raise NotImplementedError('Use add method instead.')

    def logHistory(self, message, path=None):
        """Add a new history entry based on the given message."""
        entry = HistoryEntry(message, path)
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(entry))
        self.counter += 1
        while self.counter in self:
            self.counter += 1
        key = unicode(self.counter)
        super(Logger, self).__setitem__(key, entry)

    def logError(self, message, path=None):
        """Add a new error entry based on the given message."""
        entry = ErrorEntry(message, path)
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(entry))
        self.counter += 1
        while self.counter in self:
            self.counter += 1
        key = unicode(self.counter)
        super(Logger, self).__setitem__(key, entry)

    def __repr__(self):
        return "<%s %r>" %(self.__class__.__name__, self.__name__)


class LocalLogger(Logger):
    """Local Logger."""

    zope.interface.implements(interfaces.ILocalLogger)


class MirrorLogger(Logger):
    """Mirror Logger."""

    zope.interface.implements(interfaces.IMirrorLogger)


def _getLogger(loggerFactory):
    # We use the interaction participation and the getSite hook as base concept
    # for logging. We store our ILogger instance in the LogContainer and store
    # a reference in the request annotation. This allows us to get the same
    # already stored logger instance in one transaction.
    interaction = getInteraction()
    request = interaction.participations[0]
    annotations = IAnnotations(request)
    try:
        return annotations[LOGGER_KEY]
    except KeyError:
        site = hooks.getSite()
        container = interfaces.ILogContainer(site)
        obj = loggerFactory()
        auth = zope.component.getUtility(IAuthentication)
        usr = auth['users'].queryPrincipal(request.principal.id)
        if usr is not None:
            if interfaces.IPYPIUser.providedBy(usr):
                obj.userName = '%s %s' % (usr.firstName, usr.lastName)
            else:
                obj.userName = usr.title
        else:
            obj.userName = u'System Scheduler'
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
        # add the log entry to the log container
        container.add(obj)
        # hold a reference in request annotation for adding future log entries
        annotations[LOGGER_KEY] = obj
        return obj


def getLocalLogger():
    loggerFactory = LocalLogger
    return _getLogger(loggerFactory)

def getMirrorLogger():
    loggerFactory = MirrorLogger
    return _getLogger(loggerFactory)


@zope.component.adapter(interfaces.IPYPISite)
@zope.interface.implementer(interfaces.ILogContainer)
def getLogContainer(context):
    annotations = IAnnotations(context)
    try:
        return annotations[LOG_CONTAINER_KEY]
    except KeyError:
        obj = LogContainer()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
        annotations[LOG_CONTAINER_KEY] = obj
        name = '++logger++' # not registered as traversable namespace
        zope.location.locate(annotations[LOG_CONTAINER_KEY], context, name)
        return annotations[LOG_CONTAINER_KEY]
# Help out apidoc
getLogContainer.factory = Logger
