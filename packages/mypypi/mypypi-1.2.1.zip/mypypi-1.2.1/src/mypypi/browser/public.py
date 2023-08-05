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
$Id: public.py 3362 2012-11-18 01:37:52Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import re

import zope.interface
import zope.component
import zope.event
import zope.lifecycleevent
import zope.schema
import zope.security
from zope.traversing.browser import absoluteURL
from zope.publisher.browser import BrowserPage

import z3c.tabular.table
import z3c.pagelet.browser
from z3c.template.template import getPageTemplate
from z3c.template.template import getLayoutTemplate
from z3c.form import field
from z3c.form import button
from z3c.formui import form
from z3c.table import column

import p01.fsfile.schema
import p01.fsfile.browser
import p01.fsfile.interfaces
import p01.tmp.interfaces

from mypypi.i18n import MessageFactory as _
from mypypi import interfaces
from mypypi import public
from mypypi.browser.setuptools import errorResponse


class PublicLinks(z3c.pagelet.browser.BrowserPagelet):
    """Public file management page."""

    @property
    def links(self):
        baseURL = absoluteURL(self.context, self.request)
        return [{'name':name,
                  'url': '%s/%s' % (baseURL, name),
                  #'date': self.getCreatedDate(fle),
                  }
                for name, fle in self.context.items()]


class PublicFileDownload(p01.fsfile.browser.FSFileDownload):
    """Public file download."""

    def __call__(self):
        return super(PublicFileDownload, self).__call__()
