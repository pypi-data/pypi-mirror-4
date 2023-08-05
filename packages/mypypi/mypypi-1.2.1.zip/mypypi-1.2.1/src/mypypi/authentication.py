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

import zope.interface
from zope.schema.fieldproperty import FieldProperty

from z3c.authenticator import user
from z3c.authenticator import group
from mypypi import interfaces


class PYPIUser(user.User):
    """PYPISite user (can get mapped into a gorup)."""

    zope.interface.implements(interfaces.IPYPIUser)

    firstName = FieldProperty(interfaces.IPYPIUser['firstName'])
    lastName = FieldProperty(interfaces.IPYPIUser['lastName'])
    email = FieldProperty(interfaces.IPYPIUser['email'])
    phone = FieldProperty(interfaces.IPYPIUser['phone'])

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.title)


class PYPIAdmin(PYPIUser):
    """PYPISite admin.
    
    There is only one of them per server setup. This marker is used for
    ensure that we do not remove this important user.
    """

    zope.interface.implements(interfaces.IPYPIAdmin)


class PYPIGroup(group.Group):
    """PYPISite group groups users into groups."""

    zope.interface.implements(interfaces.IPYPIGroup)
