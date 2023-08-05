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
import shutil
import datetime
import platform
import pytz
import persistent
import transaction
import BTrees.OOBTree
import binascii
import uuid
from ZODB import utils
from ZODB.interfaces import IConnection

import zope.interface
import zope.event
import zope.lifecycleevent
from zope.component import hooks
from zope.authentication.interfaces import IUnauthenticatedPrincipal
from zope.contenttype import guess_content_type
from zope.publisher.interfaces import NotFound
from zope.security.management import getInteraction
from zope.schema.fieldproperty import FieldProperty
from zope.app.appsetup.product import getProductConfiguration
from zope.container import contained

import p01.fsfile.file
from p01.fsfile import exceptions
from p01.fsfile import interfaces
from p01.fsfile.tm import FSFileStoreTransactionDataManager


def getFSStoragePath(product='p01.fsfile', confKey='storage',
    envKey='P01_FSSTORAGE_PATH'):
    path = None
    config = getProductConfiguration(product)
    if config is not None:
        path = config.get(confKey)
    else:
        path = os.environ.get(envKey)
    # tweak windows path
    if path is None:
        raise ValueError(
            "You must define %s '%s' for run this server" % (product, confKey))
    if platform.system() == 'Windows':
        # fix buildout based path setup like we do in buildout.cfg
        # ${buildout:directory}/parts/fsstorage
        parts = path.split('/')
        path = os.path.join(*parts)
    if not os.path.exists(path):
        raise exceptions.MissingStoragePathError(
            "Given storage path '%s' does not exist" % path)
    return unicode(path)


class FSStorageBase(object):
    """Very generic file system file storage base class."""
    zope.interface.implements(interfaces.IFSStorage)

    fsFileFactory = p01.fsfile.file.FSFile
    ghostFileFactory = p01.fsfile.file.GhostFile

    storageName = FieldProperty(interfaces.IFSStorage['storageName'])
    readBlockSize = FieldProperty(interfaces.IFSStorage['readBlockSize'])

    def setMetaData(self, fsFile, data):
        """Set meta data based on data dict. Normal only contentType get set.
        """
        contentType = data['contentType']
        size = data['size']
        if contentType is not None:
            fsFile.contentType = contentType
        if size is not None:
            fsFile.size = data['size']

    def remove(self, fsFile):
        """Remove a fsFile from storage."""
        self.makeGhostFile(fsFile)

    def getFileReader(self, fsFile):
        """Returns a IReadFSFile adapter adapting the given IFSFile."""
        openFile = self.getOpenFile(fsFile)
        return zope.component.getMultiAdapter((fsFile, self, openFile),
            interfaces.IFSFileReader)

    # transaction data manager
    def joinStoreTransaction(self, fsFile):
        # apply transaction manager for file system file observation
        if fsFile._p_jar is not None:
            # If we are connected to a database, then we use the
            # transaction manager that belongs to this connection
            tm = fsFile._p_jar.transaction_manager
        else:
            # If we are not connected to a database, we use the default
            tm = transaction.manager

        dm = FSFileStoreTransactionDataManager(self, fsFile, tm)
        tm.get().join(dm)

    # store transaction handler
    def voteStoreTransaction(self, fsFile):
        """Knows how to vote a store transaction."""
        pass

    def commitStoreTransaction(self, fsFile):
        """Knows how to commit a store transaction."""
        pass

    def abortStoreTransaction(self, fsFile):
        """Knows how to abort a store transaction."""
        pass

    def finishStoreTransaction(self, fsFile):
        """Knows how to finish a store transaction."""
        pass

    def makeGhostFile(self, fsFile):
        """Make a ghost file from a given file."""
        raise NotImplementedError('Sub class must implement makeGhostFile.')

    def removeGhostFiles(self):
        """Remove ghost files."""
        raise NotImplementedError('Sub class must implement removeGhostFiles.')

    def removeGhostFile(self, fsID):
        """Remove one ghost file by it's fsID."""
        raise NotImplementedError('Sub class must implement removeGhostFiles.')

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.storageName)


class TMPFileConsumerBase(object):
    """TMPFile consumer support.

    This mixin class provides a ITMPFile based store concept.
     """

    zope.interface.implements(interfaces.ITMPFileConsumer)

    def _storeFSFileData(self, tmpFile, fsFile):
        """move file to it's new location."""
        try:
            if not tmpFile.closed:
                tmpFile.close()
            # move real file used by tmpFile to the new path
            shutil.move(tmpFile.tmpPath, fsFile.path)
            # we moved it, but act as it's been gone
            tmpFile.release()
        except OSError:
            raise exceptions.FSFileProcessingError("File move operation failed")

    def setFileName(self, fsFile, fileName, fsNameSpace=None):
        # set the filename given from file upload, this is usable for widgets
        # and container __setitem__ methods
        fsFile.__name__ = fileName

    def store(self, tmpFile, fileName=None, fsNameSpace=None,
        fsFileFactory=None):
        """Store a fsFile in the file system and return a IFSFile instance."""
        if fsFileFactory is None:
            fsFileFactory = self.fsFileFactory

        # create FSFile, this allows to use the _p_oid etc in _getFSID
        fsFile = fsFileFactory()

        # notify created
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(fsFile))

        # join transaction
        self.joinStoreTransaction(fsFile)

        # set the filename given from file upload, this is usable for widgets
        # and container __setitem__ methods
        self.setFileName(fsFile, fileName, fsNameSpace)

        # generate fsID
        fsID = self._getFSID(fsFile, fileName, fsNameSpace)
        # apply fsID
        fsFile.fsID = fsID
        # apply storageName which acts as the binding to the right named
        # storage utility.
        fsFile.fsStorageName = self.storageName
        # set namespace if given
        if fsNameSpace is not None:
            fsFile.fsNameSpace = fsNameSpace

        # store IFSFile in backend
        self._storeFSFileData(tmpFile, fsFile)

        # get meta data
        size = self.getSize(fsFile)
        contentType = self.getContentType(fsFile)

        # set meta data
        data = {'fsID': fsID, 'fileName': fileName, 'size': size,
                'contentType': contentType}
        self.setMetaData(fsFile, data)

        return fsFile


class FSPathStorageBase(FSStorageBase):
    """File system storage base class.

    One limitation of this storage is the file per directory limitation.
    Make sure your file system allows to store the amount of files you like to
    store.

    This storage is only a prove of concept. But we use it in mypypi as backend
    and will fit for similar usecases.
    """

    def __init__(self, path):
        # setup path
        path = unicode(path)
        if not os.path.exists(path):
            os.mkdir(path, 0700)
        self.path = os.path.abspath(path)

    def getStorageDir(self, fsNameSpace=None):
        """Get the storage directory."""
        raise NotImplementedError('Sub class must implement getStorageDir')

    def _getFSID(self, fsFile, fileName=None, fsNameSpace=None):
        """Knows how to generate the fsID."""
        # our fsID in this storage is the real file system file path. Let's
        # generate a unique filename
        now = datetime.datetime.now(pytz.UTC)
        postFix = '%s.%3d' % (now.strftime("%Y%m%d-%H-%M-%S"),
            now.microsecond / 1000)
        if fileName is None:
            #there might be a race condition around this
            #but doing this right needs quite a bit of infrastructure
            #(that also depends on the platform)
            #that would contain also some locking on the file system
            fileName = str(uuid.uuid1())

        fileName = '%s-%s' % (fileName, postFix)
        dirPath = self.getStorageDir(fsNameSpace)
        path = os.path.join(dirPath, fileName)
        if os.path.exists(path):
            raise exceptions.DuplicatedFSFilePathError(
                "File '%s' already exist in storage" % fileName)
        return fileName

    def getOpenFile(self, fsFile):
        """Returns an open file based on the given IFSFile or raises NotFound.
        """
        if fsFile.isGhost:
            raise NotFound(self, fsFile.fsID)
        if not os.path.exists(fsFile.path):
            raise NotFound(self, fsFile.fsID)
        return open(fsFile.path, 'rb')

    def getSize(self, fsFile):
        """Set meta data based on data dict. Normal only contentType get set.
        """
        # our fsID in this storage is the real file system file path
        return os.path.getsize(fsFile.path)

    def getContentType(self, fsFile):
        """Get content type for given fsFile."""
        if fsFile.__name__ is not None:
            return guess_content_type(fsFile.__name__)[0]

    def abortStoreTransaction(self, fsFile):
        """Knows how to abort a store transaction."""
        if fsFile.fsID is not None and os.path.isfile(fsFile.path):
            try:
                os.remove(fsFile.path)
            except OSError:
                # ignore file system erros and add it to the ghost files
                self.makeGhostFile(fsFile)

    def makeGhostFile(self, fsFile):
        ghostFile = self.ghostFileFactory(fsFile)
        fsFile.isGhost = True
        self._ghostFiles[fsFile.fsID] = ghostFile

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

    def __repr__(self):
        return "<%s %r at %r>" % (self.__class__.__name__, self.storageName,
            self.path)


class FlatPathFSStorageBase(FSPathStorageBase):
    """Flat file system storage base with namespace support."""
    zope.interface.implements(interfaces.IFlatPathFSStorage)

    path = FieldProperty(interfaces.IFlatPathFSStorage['path'])

    def _getFilenameForOID(self, oid):
        """Given an OID, return a filename on the filesystem where
        the blob data relating to that OID is stored.
        """
        # OIDs are numbers and sometimes passed around as integers. For our
        # computations we rely on the 64-bit packed string representation.
        if isinstance(oid, int):
            oid = utils.p64(oid)

        fname = '_'.join(['0x%s' % binascii.hexlify(byte) for byte in str(oid)])
        return fname

    def _getZODBConnection(self):
        """Returns a ZODB connection based on the site."""
        site = hooks.getSite()
        return IConnection(site)

    def _getFSID(self, fsFile, fileName=None, fsNameSpace=None):
        oid = fsFile._p_oid
        if oid is None:
            # add the fsFile to the DB which will add an oid
            connection = self._getZODBConnection()
            connection.add(fsFile)
            oid = fsFile._p_oid
        # ignore file name and namespace and generate a unique file name which
        # is needed for ghost file support
        now = datetime.datetime.now(pytz.UTC)
        fileName = '%s.%3d' % (now.strftime("%Y%m%d-%H-%M-%S"),
            now.microsecond / 1000)
        oidPath = self._getFilenameForOID(oid)
        return u"%s-%s" % (oidPath, fileName)

    def getStorageDir(self, fsNameSpace=None):
        """Get the storage directory."""
        if fsNameSpace is None:
            return self.path
        path = self.path
        names = fsNameSpace.split('/')
        for name in names:
            newPath = os.path.join(path, name)
            if not os.path.exists(newPath):
                os.mkdir(newPath, 0700)
        return os.path.abspath(newPath)


class FlatPathFSStorage(FlatPathFSStorageBase, TMPFileConsumerBase,
    persistent.Persistent, contained.Contained):
    """Persistent flat file system storage with built in ghost file support."""

    def __init__(self, path):
        super(FlatPathFSStorage, self).__init__(path)
        # setup ghost file storage
        self._ghostFiles = BTrees.OOBTree.OOBTree()

    def _getZODBConnection(self):
        """Returns a ZODB connection based on self."""
        return IConnection(self)


class UserPathFSStorageBase(FSPathStorageBase):
    """User based file system storage base class."""
    zope.interface.implements(interfaces.IUserPathFSStorage)

    path = FieldProperty(interfaces.IUserPathFSStorage['path'])
    userPath = FieldProperty(interfaces.IUserPathFSStorage['userPath'])
    sharePath = FieldProperty(interfaces.IUserPathFSStorage['sharePath'])

    def __init__(self, path):
        super(UserPathFSStorageBase, self).__init__(path)
        # setup share dir
        sharePath = os.path.join(self.path, 'share')
        if not os.path.exists(sharePath):
            os.mkdir(sharePath, 0700)
        self.sharePath = os.path.abspath(sharePath)

        # setup user dir
        userPath = os.path.join(self.path, 'user')
        if not os.path.exists(userPath):
            os.mkdir(userPath, 0700)
        self.userPath = os.path.abspath(userPath)

    def _getZODBConnection(self):
        """Returns a ZODB connection based on the site."""
        site = hooks.getSite()
        return IConnection(site)

    def getStorageDir(self, fsNameSpace=None):
        """Get the storage directory."""
        if fsNameSpace is not None:
            path = self.path
            names = fsNameSpace.split('/')
            for name in names:
                newPath = os.path.join(path, name)
                if not os.path.exists(newPath):
                    os.mkdir(newPath, 0700)
            return os.path.abspath(newPath)
        request = getInteraction().participations[0]
        if IUnauthenticatedPrincipal.providedBy(request.principal):
            dirPath = self.sharePath
        else:
            #XXX: what's `key` here???
            dirPath = os.path.join(self.userPath, key)
            if not os.path.exists(dirPath):
                os.mkdir(dirPath, 0700)

        return os.path.abspath(dirPath)


class UserPathFSStorage(UserPathFSStorageBase, TMPFileConsumerBase,
    persistent.Persistent, contained.Contained):
    """Persistent user based file system storage with built in ghost file
    support.
    """

    def __init__(self, path):
        super(UserPathFSStorage, self).__init__(path)
        # setup ghost file storage
        self._ghostFiles = BTrees.OOBTree.OOBTree()


class BushyFSStorageBase(FSPathStorageBase):
    """A bushy directory file system storage base class.

    Creates an 8-level directory structure (one level per byte) in
    big-endian order from the OID of an object.

    """
    zope.interface.implements(interfaces.IBushyFSStorage)

    path = FieldProperty(interfaces.IBushyFSStorage['path'])

    def getStorageDir(self, fsNameSpace=None):
        """Ignore fsNameSpace and return the storage directory."""
        return self.path

    def _getPathForOID(self, oid, create=False):
        """Given an OID, return the path on the filesystem where
        the blob data relating to that OID is stored.

        If the create flag is given, the path is also created if it didn't
        exist already.

        """
        # OIDs are numbers and sometimes passed around as integers. For our
        # computations we rely on the 64-bit packed string representation.
        if isinstance(oid, int):
            oid = utils.p64(oid)

        directories = []
        # Create the bushy directory structure with the least significant byte
        # first
        for byte in str(oid):
            directories.append('0x%s' % binascii.hexlify(byte))
        relPath = os.path.sep.join(directories)
        path = self.getStorageDir()
        oidPath = os.path.join(path, relPath)
        if create and not os.path.exists(oidPath):
            try:
                os.makedirs(oidPath, 0700)
            except OSError:
                # we might have lost a race
                try:
                    assert os.path.exists(oidPath)
                except AssertionError:
                    # the directory  must exist now
                    raise ValueError("Path %r doesn't exist" % oidPath)
        return unicode(relPath)

    def _getZODBConnection(self):
        """Returns a ZODB connection based on the site."""
        site = hooks.getSite()
        return IConnection(site)

    def _getOIDForPath(self, oidPath):
        """Given a path, return an OID, if the path is a valid path for an
        OID. The inverse function to `_getPathForOID`.

        Raises ValueError if the path is not valid for an OID.

        """
        path = self.getStorageDir()
        relPath = oidPath[len(path):]
        pattern = re.compile(
            r'(0x[0-9a-f]{1,2}\%s){7,7}0x[0-9a-f]{1,2}$' % os.path.sep)
        if pattern.match(relPath) is None:
            raise ValueError("Not a valid OID path: `%s`" % relPath)
        pathList = relPath.split(os.path.sep)
        # Each path segment stores a byte in hex representation. Turn it into
        # an int and then get the character for our byte string.
        oid = ''.join(binascii.unhexlify(byte[2:]) for byte in pathList)
        return oid

    def _getFSID(self, fsFile, fileName=None, fsNameSpace=None):
        oid = fsFile._p_oid
        if oid is None:
            # add the fsFile to the DB which will add an oid
            connection = self._getZODBConnection()
            connection.add(fsFile)
            oid = fsFile._p_oid
        # ignore file name and namespace and generate a unique file name which
        # is needed for ghost file support
        now = datetime.datetime.now(pytz.UTC)
        fileName = '%s.%3d' % (now.strftime("%Y%m%d-%H-%M-%S"),
            now.microsecond / 1000)
        oidPath = self._getPathForOID(oid, True)
        return os.path.join(oidPath, fileName)


class BushyFSStorage(BushyFSStorageBase, TMPFileConsumerBase,
    persistent.Persistent, contained.Contained):
    """Persistent bushy directory file system storage with built in ghost file
    support.
    """

    def __init__(self, path):
        super(BushyFSStorage, self).__init__(path)
        # setup ghost file storage
        self._ghostFiles = BTrees.OOBTree.OOBTree()

    def _getZODBConnection(self):
        """Returns a ZODB connection based on self."""
        return IConnection(self)
