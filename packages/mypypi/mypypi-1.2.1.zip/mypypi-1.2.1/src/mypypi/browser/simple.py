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

import zope.component
from zope.publisher.interfaces import NotFound
from zope.traversing.browser import absoluteURL

import mypypi.api
import mypypi.browser



class SimpleIndex(mypypi.browser.IndexPageBase):
    """Simple (package links) index."""

    @property
    def title(self):
        return self.context.title

    def publishTraverse(self, request, name):
        # make this view traversable, this allows us to traverse to the pkg
        pkg = self.context.get(name)
        if pkg is None:
            if '-' in name:
                name = name.replace('-', '_')
                pkg = self.context.get(name)

                if pkg is None:
                    raise NotFound(self, name, request)
            else:
                raise NotFound(self, name, request)
        # get the index.html view for this package
        view = zope.component.queryMultiAdapter((pkg, request),
            name='simpleDetail')
        if view is None:
            raise NotFound(self, name, request)
        return view

    @property
    def links(self):
        simpleURL = '%s/simple' % absoluteURL(self.context, self.request)
        return [mypypi.api.renderOneLineLink(
                    '%s/%s' % (simpleURL, name), name)
                for name, pkg in self.context.items()
                if mypypi.api.checkViewable(pkg)]


class SimpleDetail(mypypi.browser.IndexPageBase):
    """Simple (release links) detail page."""

    @property
    def title(self):
        return self.context.__name__

    @property
    def links(self):
        res = []
        for release in self.context.values():
            releaseURL = absoluteURL(release, self.request)
            res += [mypypi.api.renderOneLineLink(
                        '%s/%s' % (releaseURL, rFile.__name__), rFile.__name__)
                    for rFile in release.values()
                    if mypypi.api.checkViewable(rFile)]
        return res
