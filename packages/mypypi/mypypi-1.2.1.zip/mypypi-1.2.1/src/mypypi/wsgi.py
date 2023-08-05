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

import os
import zope.event
import zope.app.wsgi
import zope.app.appsetup.interfaces


def application_factory(global_conf, conf='zope.conf', **local_conf):
    configfile = os.path.join(global_conf['here'], conf)
    schemafile = os.path.join(
        os.path.dirname(zope.app.appsetup.__file__), 'schema', 'schema.xml')
    global APPLICATION
    APPLICATION = zope.app.wsgi.getWSGIApplication(configfile, schemafile)
    zope.event.notify(zope.app.appsetup.interfaces.ProcessStarting())
    return APPLICATION
