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
$Id: context.py 420 2007-04-08 13:49:39Z roger.ineichen $
"""

from zope.contentprovider.interfaces import IContentProvider


class IAddMenu(IContentProvider):
    """Add menu item controlling tab."""


class IServerMenu(IContentProvider):
    """Server menu item controlling tab."""


class IContextMenu(IContentProvider):
    """Context menu item controlling tab."""
