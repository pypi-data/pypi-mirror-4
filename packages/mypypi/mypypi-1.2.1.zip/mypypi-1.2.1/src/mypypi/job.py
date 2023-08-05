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
$Id: login.py 411 2007-04-01 05:11:53Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import logging

import zope.interface

from p01.remote import job

from mypypi import interfaces

log = logging.getLogger('mypypi')


class SyncMirrorPackages(job.Job):
    """Calls syncMirrorPackages on PYPISite as a cron job."""

    zope.interface.implements(interfaces.ISyncMirrorPackages)

    def __call__(self, remoteProcessor):
        # sync packages, our remote queue is the IPYPISite
        remoteProcessor.syncMirrorPackages()
