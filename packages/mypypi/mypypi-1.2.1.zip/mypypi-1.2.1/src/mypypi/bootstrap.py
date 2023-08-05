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

import transaction
import logging

import zope.event
import zope.lifecycleevent

from zope.app.appsetup.bootstrap import getInformationFromEvent
from zope.app.appsetup.interfaces import IDatabaseOpenedWithRootEvent
from zope.app.appsetup.interfaces import DatabaseOpenedWithRoot
from zope.app.publication.zopepublication import ZopePublication

from z3c.configurator import configurator

from mypypi import interfaces
from mypypi import site

log = logging.getLogger('mypypi')


def bootstrapPYPISite(event):
    """Subscriber to the IDataBaseOpenedEvent

    Setup a PYPISite during server startup if not given. If a site root is
    given which doesn't provide IPYPISite raise an exception.
    """
    db, connection, root, root_folder = getInformationFromEvent(event)

    if root_folder is None:
        # create
        pypiSite = site.PYPISite()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(pypiSite))

        # add as Application root
        root[ZopePublication.root_name] = pypiSite

        # just adapt which will setup the annotation containers
        interfaces.ILogContainer(pypiSite)

        # commit site to DB
        transaction.commit()

        # configure and apply SiteManager
        configurator.configure(pypiSite, None)

        # commit to DB again
        transaction.commit()

    elif root_folder is not None and not \
        interfaces.IPYPISite.providedBy(root_folder):
        raise ValueError('There is already an Application root folder in the DB '
                         'use a clean empty ZODB at server startup.')

    connection.close()

    zope.event.notify(DatabaseOpenedWithRoot(db))


@zope.component.adapter(IDatabaseOpenedWithRootEvent)
def autoStartMirrorScheduler(event):
    """Start the queue processing scheduler."""
    db = event.database
    connection = db.open()
    root = connection.root()
    pypiSite = root.get(ZopePublication.root_name, None)

    if pypiSite is not None and pypiSite.autoStartMirrorScheduler and \
        not pypiSite.isProcessing:
        pypiSite.startProcessing()
        log.info('MyPyPi Mirror Scheduler started')
