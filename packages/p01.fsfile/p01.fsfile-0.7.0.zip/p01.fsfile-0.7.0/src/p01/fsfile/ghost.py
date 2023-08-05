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

import os
import persistent
import BTrees.OOBTree

import zope.interface
from zope.container import contained

import p01.fsfile.file
from p01.fsfile import interfaces


class GhostFiles(persistent.Persistent, contained.Contained):
    """Persistent ghost file storage."""

    zope.interface.implements(interfaces.IGhostFiles)

    ghostFileFactory = p01.fsfile.file.GhostFile

    def __init__(self):
        self._ghostFiles = BTrees.OOBTree.OOBTree()

    def makeGhostFile(self, fsFile):
        fsFile.isGhost = True
        ghostFile = self.ghostFileFactory(fsFile)
        self._ghostFiles[fsFile.fsID] = ghostFile

# TODO: implement transaction support, only remove in transaction commit
    def removeGhostFiles(self):
        removedKeys = []
        append = removedKeys.append
        for key, gFile in self._ghostFiles.items():
            if os.path.exists(gFile.path):
                try:
                    os.remove(gFile.path)
                    append(key)
                except OSError:
                    # we silently ignore permission denied errros because this
                    # error message forces to keep an open file handle, how bad.
                    pass
        [self._ghostFiles.__delitem__(key) for key in removedKeys]


class GhostFileSupport(object):
    """Ghost file support mixin for non persistent FSFileStorage.

    Using an IGhostFiles utility for non persistent global FSFileStorage
    implementations.

    """

    zope.interface.implements(interfaces.IGhostFileSupport)

    def makeGhostFile(self, fsFile):
        ghostFiles = zope.component.getUtility(interfaces.IGhostFiles)
        ghostFiles.makeGhostFile(fsFile)

    def removeGhostFiles(self):
        ghostFiles = zope.component.getUtility(interfaces.IGhostFiles)
        ghostFiles.removeGhostFiles()
