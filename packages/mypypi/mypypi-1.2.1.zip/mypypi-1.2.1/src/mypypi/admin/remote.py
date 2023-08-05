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

from zope.traversing.browser import absoluteURL

from z3c.form import field
from z3c.form import button
from z3c.formui import form
from z3c.template.template import getPageTemplate

import p01.remote.browser.job
import p01.remote.browser.scheduler

from mypypi import interfaces
from mypypi import job
from mypypi import browser
from mypypi.i18n import MessageFactory as _


class CronSchedulerAddFrom(p01.remote.browser.scheduler.CronSchedulerAddFrom):
    """Cron scheduler job add form."""

    template = getPageTemplate(name='simple')


class SyncMirrorPackagesProcessFrom(p01.remote.browser.job.JobProcessFrom):

    label = _('Process Mirror Scheduler Job')


class SyncMirrorPackagesAddFrom(form.AddForm):
    """Mirror scheduler job add form."""

    template = getPageTemplate(name='simple')

    buttons = form.AddForm.buttons.copy()
    handlers = form.AddForm.handlers.copy()

    label = _('Add Sync Mirror Packages Scheduler')

    fields = field.Fields(interfaces.ISyncMirrorPackages).select('__name__')

    def createAndAdd(self, data):
        __name__ = data['__name__']
        mirrorJob = job.SyncMirrorPackages()
        jobid = self.context.addJob(__name__, mirrorJob)
        self._finishedAdd = True
        return jobid

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.getURL())

    def nextURL(self):
        return '%s/jobs.html' % absoluteURL(self.context, self.request)
