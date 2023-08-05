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

import z3c.layer.ready2go
import p01.fswidget.layer
import p01.remote.layer
import p01.zmi.layer


class IPYPICoreLayer(p01.fswidget.layer.IFSWidgetBrowserLayer,
    p01.remote.layer.IRemoteBrowserLayer,
    z3c.layer.ready2go.IReady2GoBrowserLayer):
    """The Pypi application layer."""


class IPYPIBrowserLayer(IPYPICoreLayer, p01.zmi.layer.IZMIBrowserLayer):
    """The Pypi browser layer."""
