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

import unittest
from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite

from z3c.testing import InterfaceBaseTest

from mypypi import interfaces
from mypypi import site
from mypypi import package
from mypypi import release
from mypypi import testing


class SiteTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IPYPISite

    def getTestClass(self):
        return site.PYPISite


class LocalPackageTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ILocalPackage

    def getTestClass(self):
        return package.LocalPackage


class MirrorPackageTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IMirrorPackage

    def getTestClass(self):
        return package.MirrorPackage

    def getTestPos(self):
        return ('http://pypy.python.org/pypi',)


class LocalReleaseTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ILocalRelease

    def getTestClass(self):
        return release.LocalRelease


class MirrorReleaseTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IMirrorRelease

    def getTestClass(self):
        return release.MirrorRelease


def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
            setUp=testing.placefulSetUp,
            tearDown=testing.placefulTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        unittest.makeSuite(SiteTest),
        unittest.makeSuite(LocalPackageTest),
        unittest.makeSuite(MirrorPackageTest),
        unittest.makeSuite(LocalReleaseTest),
        unittest.makeSuite(MirrorReleaseTest),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
