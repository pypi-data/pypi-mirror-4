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
$Id: __init__.py 451 2007-05-13 02:54:09Z roger.ineichen $
"""

import zope.interface
import zope.component
from zope.traversing.browser import absoluteURL
from zope.component import hooks
from zope.app.security.interfaces import IUnauthenticatedPrincipal

from z3c.template.template import getPageTemplate

import mypypi.layer
from mypypi import interfaces
from mypypi.skin import IHeaderProvider


class HeaderProvider(object):
    """Header content provider."""

    zope.interface.implements(IHeaderProvider)
    zope.component.adapts(zope.interface.Interface,
        mypypi.layer.IPYPIBrowserLayer, zope.interface.Interface)

    anonymousTemplate = getPageTemplate('anonymous')
    authenticatedTemplate = getPageTemplate('authenticated')

    def __init__(self, context, request, view):
        self.__parent__ = view
        self.context = context
        self.request = request

    @property
    def searchURL(self):
        site = hooks.getSite()
        siteURL = absoluteURL(site, self.request)
        if interfaces.IPYPIPage.providedBy(self.__parent__):
            return '%s/pypi/search.html' % siteURL
        return '%s/search.html' % siteURL

    def update(self):
        pass

    def render(self):
        self.update()
        if IUnauthenticatedPrincipal.providedBy(self.request.principal):
            return self.anonymousTemplate()
        else:
            return self.authenticatedTemplate()
