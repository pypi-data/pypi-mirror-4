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
$Id: eggs.py 2199 2011-01-03 14:31:45Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

from zope.traversing.browser import absoluteURL

import mypypi.api
import mypypi.browser


class Eggs(mypypi.browser.IndexPageBase):
    """Eggs - flat list of all available eggs"""

    @property
    def title(self):
        return self.context.title

    @property
    def links(self):
        rv = []
        for name, pkg in self.context.items():
            if mypypi.api.checkViewable(pkg):
                for rname, rel in pkg.items():
                    if mypypi.api.checkViewable(rel):
                        for fname, fle in rel.items():
                            rv.append(mypypi.api.renderOneLineLink(
                                absoluteURL(fle, self.request), fname))
        return rv
