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

import zope.interface
import zope.component
from zope.schema.fieldproperty import FieldProperty
from zope.container.interfaces import IObjectRemovedEvent
from zope.container import contained

from p01.fsfile import interfaces


class FSFile(persistent.Persistent, contained.Contained):
    """File system file.

    This file system file implementation only stores the required information
    which the relevant IFSStorage needs for identify the real file content.

    Never create and add such a file, this should always be done by a storage.

    A storage knows how to generate the required fsID and probably a
    fsNameSpace. The storage knows how to store and get the real file data for
    such a IFSFile implementation. See IFSStorage store and getFileReader
    methods.

    The storage is responsible for all file handle related operations for
    such a IFSFile.

    Remember, the IFSStorage uses transaction data managers which will protect
    the real file system file operations. Take care if you manipulate the
    IFSFile arguments directly. Probably this should never happen. If you
    need to manipulate the fsID, fsNameSpace or fsStorageName you should
    probably add a method to our storage and delegate the manipulation part to
    this storage method. Also note, the storage provides hooks which the
    transaction data manager will call. Probably you can use such a method for
    implement what you need.

    Summary:

    The FSFile implementation is only responsible for let a IFSStorage
    indentify the right file data in the storage. Every file data manipulation
    should be done in a FSStorage method (deleation pattern). Because only the
    FSStorage could know how to do it right. Keep in mind that the FSFile is
    observed by a transaction manager.
    """

    zope.interface.implements(interfaces.IFSFile)

    contentType = FieldProperty(interfaces.IFSFile['contentType'])
    size = FieldProperty(interfaces.IFSFile['size'])

    fsID = FieldProperty(interfaces.IFSFile['fsID'])
    fsNameSpace = FieldProperty(interfaces.IFSFile['fsNameSpace'])
    fsStorageName = FieldProperty(interfaces.IFSFile['fsStorageName'])

    isGhost = FieldProperty(interfaces.IFSFile['isGhost'])

    def __init__(self, fsID=None, fsStorageName=None, fsNameSpace=None):
        """Stores file storage and file information for accessing file data."""
        super(FSFile, self).__init__()
        if fsID is not None:
            self.fsID = fsID
        if fsStorageName is not None:
            self.fsStorageName = fsStorageName
        if fsNameSpace is not None:
            self.fsNameSpace = fsNameSpace

    @property
    def path(self):
        storage = zope.component.getUtility(interfaces.IFSStorage,
            name=self.fsStorageName)
        return os.path.join(storage.getStorageDir(self.fsNameSpace), self.fsID)

    def __repr__(self):
        return "<%s, %s fsID %r in %r ns %r>" % (self.__class__.__name__,
            self.__name__, self.fsID,
            self.fsStorageName, self.fsNameSpace or u'')


class GhostFile(persistent.Persistent, contained.Contained):
    """Ghost file storing the fsID etc. from a removed file."""

    zope.interface.implements(interfaces.IGhostFile)

    contentType = FieldProperty(interfaces.IGhostFile['contentType'])
    size = FieldProperty(interfaces.IGhostFile['size'])

    _fsID = FieldProperty(interfaces.IGhostFile['fsID'])
    _fsNameSpace = FieldProperty(interfaces.IGhostFile['fsNameSpace'])
    _fsStorageName = FieldProperty(interfaces.IGhostFile['fsStorageName'])

    def __init__(self, fsFile):
        """Stores file storage and file information for accessing file data."""
        super(GhostFile, self).__init__()
        self._fsID = fsFile.fsID
        self._fsStorageName = fsFile.fsStorageName
        if fsFile.fsNameSpace is not None:
            self._fsNameSpace = fsFile.fsNameSpace

    @property
    def fsID(self):
        # read only
        return self._fsID

    @property
    def fsNameSpace(self):
        # read only
        return self._fsNameSpace

    @property
    def fsStorageName(self):
        # read only
        return self._fsStorageName

    @property
    def path(self):
        storage = zope.component.getUtility(interfaces.IFSStorage,
            name=self.fsStorageName)
        return os.path.join(storage.path, self.fsID)

    def __repr__(self):
        return "<%s, %s fsID %r in %r ns %r>" % (self.__class__.__name__,
            self.__name__, self.fsID,
            self.fsStorageName, self.fsNameSpace or u'')


class FSFileReader(object):
    """Default read adapter for IFSFile.

    Note, you can only read a file once. Seeking is not supported.
    """

    zope.component.adapts(interfaces.IFSFile, interfaces.IFSStorage,
        zope.interface.Interface)
    zope.interface.implements(interfaces.IFSFileReader)

    def __init__(self, context, storage, fileHandle):
        self.context = context
        self.storage = storage
        self._file = fileHandle
        self._closed = False

    def close(self):
        if not self._closed:
            self._file.close()
            # let the grabage collector remove the file handle
            self._file = None
            self._closed = True

    def read(self, blocksize=None):
        """Support for special wsgi.file_wrapper.

        The WSGI spec says. To be considered "file-like", the object supplied
        by the application must have a read() method that takes an optional
        size argument. (only used by special wsgi.file_wrapper)
        """
        if self._closed:
            raise ValueError('I/O operation on closed file')
        if blocksize is None:
            blocksize = self.storage.readBlockSize
        # be aware of that this method reads the file into the memory. But
        # we have to ensure to close the file handle which will simplify the
        # file handling and is smarter to file handles. Probably there is a
        # better way to do this and ensure to close a file.
        mem = self._file.read(blocksize)
        self._file.close()
        self._closed = True
        return mem

    def __iter__(self):
        """Take care on closing the file."""
        if self._closed:
            raise ValueError('I/O operation on closed file')
        f = self._file
        while 1:
            v = f.read(self.storage.readBlockSize)
            if v:
                yield v
            else:
                self.close()
                break

    def __repr__(self):
        return "<%s for %r from %r>" % (self.__class__.__name__,
            self.context.fsID, self.context.fsStorageName)


@zope.component.adapter(interfaces.IFSFile)
@zope.interface.implementer(interfaces.IFSFileReader)
def getFileReader(fsFile):
    """Returns a FileReader providing an open file handle from storage.

    This adapter hook allows to adapt an IFSFile and will lookup a real
    IFSFileReader adapting (IFSFile, IFSStorage, openFile). This gives us
    simpler access to the file reader by adapting the single IFSFile.
    """
    storage = zope.component.getUtility(interfaces.IFSStorage,
        name=fsFile.fsStorageName)
    return storage.getFileReader(fsFile)


@zope.component.adapter(interfaces.IFSFile, IObjectRemovedEvent)
def fsFileRemoveHandler(fsFile, event):
    """Remove the file system file from storage with transaction control."""
    storage = zope.component.getUtility(interfaces.IFSStorage,
        name=fsFile.fsStorageName)
    # call storage remove which will apply our remove transaction manager
    storage.remove(fsFile)
