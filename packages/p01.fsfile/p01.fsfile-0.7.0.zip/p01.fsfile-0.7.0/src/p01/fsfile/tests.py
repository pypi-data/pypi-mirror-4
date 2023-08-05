##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
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

import re
import os
import sys
import unittest
import zope.component
from zope.testing import doctest
from zope.testing import renormalizing
from zope.testing.doctestunit import DocFileSuite

import z3c.testing

from p01.fsfile import interfaces
from p01.fsfile import testing
from p01.fsfile.file import FSFile
from p01.fsfile.storage import getFSStoragePath
from p01.fsfile.storage import FlatPathFSStorage
from p01.fsfile.storage import UserPathFSStorage


checker = renormalizing.RENormalizing([
    (re.compile('\\\\'), '/'),
    (re.compile('//'), '/'),
    ])


class StorageStub(object):
    zope.interface.implements(interfaces.IFSStorage)

    def getStorageDir(self, fsNameSpace=None):
        return u''


class TestFSFile(z3c.testing.InterfaceBaseTest):

    def setUp(self):
        zope.component.provideUtility(StorageStub(), name=u'storageName')

    def getTestInterface(self):
        return interfaces.IFSFile

    def getTestClass(self):
        return FSFile

    def getTestPos(self):
        return (u'fsID', u'storageName')


class TestFSPathStorage(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IFSStorage

    def getTestClass(self):
        return FlatPathFSStorage

    def getTestPos(self):
        path = getFSStoragePath()
        storagePath = os.path.join(path, 'tests')
        return (storagePath,)


def test_suite():
    suite = (
        DocFileSuite('README.txt',
            setUp=testing.doctestSetUp, tearDown=testing.doctestTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker
            ),
        unittest.makeSuite(TestFSFile),
        unittest.makeSuite(TestFSPathStorage),
        )
    if sys.platform == 'win32':
        suite += (
        DocFileSuite('openfile_windows.txt',
            setUp=testing.doctestSetUp, tearDown=testing.doctestTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker
            ),
        )
    return unittest.TestSuite(suite)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
