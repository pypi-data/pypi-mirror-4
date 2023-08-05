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

from zope.publisher.browser import BrowserPage

import mypypi.api


class IndexPageBase(BrowserPage):
    """Simple page for rendering title, body wihtout anything else"""

    @property
    def title(self):
        return self.context.__name__

    @property
    def body(self):
        return '<br />\n'.join(self.links)

    def __call__(self):
        return mypypi.api.renderPage(self)
