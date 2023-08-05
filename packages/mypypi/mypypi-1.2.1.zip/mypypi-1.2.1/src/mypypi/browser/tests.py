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
$Id: tests.py 1504 2009-10-19 12:51:39Z adam.groszer $
"""

import unittest

from mypypi import testing


def test_suite():
    suite = unittest.TestSuite((
        testing.FunctionalDocFileSuite('setuptools.txt'),
        testing.FunctionalDocFileSuite('mirror.txt'),
        testing.FunctionalDocFileSuite('keasbuild.txt'),
        ))

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')