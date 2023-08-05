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

import zope.interface
import zope.schema
import zope.i18nmessageid
import zope.configuration.fields
from zope.publisher.interfaces.http import IResult

_ = zope.i18nmessageid.MessageFactory('p01')


def isDirectory(path):
    return os.path.isdir(path)


class IFSFile(zope.interface.Interface):
    """File system file without ILocation.

    Note: This interface doens't provide ILocation or IContained. The missing
    ILocation interface in this interface makes it simpler for define correct
    permissions in ZCML.
    """

    fsID = zope.schema.TextLine(
        title=_(u'File system file identifier'),
        description=_(u'File system file identifier used by the storage.'),
        default=None)

    path = zope.schema.TextLine(
        title=_(u'Path to the file'),
        description=_(u'Path to the file.'),
        readonly=True,
        default=None)

    fsStorageName = zope.schema.TextLine(
        title=_(u'Storage Name'),
        description=_(u'Storage Name'),
        default=u'',
        readonly=True)

    fsNameSpace = zope.schema.TextLine(
        title=_(u'Namespace'),
        description=_(u'Namespace'),
        default=None,
        readonly=True)

    size = zope.schema.Int(
        title=_(u'Size'),
        description=_(u'The file size.'),
        default=0,
        required=True)

    contentType = zope.schema.BytesLine(
        title=_(u'Content Type'),
        description=_(u'The content type identifies the type of data.'),
        missing_value='',
        default='',
        required=False)

    isGhost = zope.schema.Bool(
        title=_(u'Is ghost file'),
        description=_(u'Is ghost file.'),
        default=False,
        required=True)


class IGhostFile(IFSFile):
    """Ghost file storing the fsID etc. from a removed file."""


class IFSFileReader(IResult):
    """Read adapter for IFSFile adapter which also provides IResult."""

    def close():
        """Close an open file handle."""

    def read(blocksize=None):
        """Read from open file handle."""


class IGhostFileSupport(zope.interface.Interface):
    """File system storage with ghost file support.

    A storage providing IGhostFile handling offers different benefits.
    One benefit could be that we can keep the file in the file system till
    we pack our ZODB. Another benefit could be, that we can remove ghost files
    in another transaction and not directly if we remove the file.
    """

    def makeGhostFile(fsFile):
        """Make a ghost file from a given file.

        This is usefull if remove a file can conflict because of open file
        handle. Mostly given based if a real filesystem backend is used.
        Ghost files must explicit get removed in another transaction after
        we are sure there is no open file handle.

        This ghost files also allow us to provide the old file if we need to
        support undo.
        """

    def removeGhostFiles():
        """Remove ghost files."""

    def removeGhostFile(fsID):
        """Remove one ghost file by it's fsID."""


class IGhostFiles(IGhostFileSupport):
    """Ghost file storage."""


class IFSStorageTransationSupport(zope.interface.Interface):
    """Transaction support for IFSStorage."""

    # transaction data manager
    def joinStoreTransaction(fsFile):
        """Apply transaction manager for file system file store observation
        to the given fsFile.
        """

    # store transaction handler
    def voteStoreTransaction(fsFile):
        """Knows how to vote a store transaction."""

    def commitStoreTransaction(fsFile):
        """Knows how to commit a store transaction."""

    def abortStoreTransaction(fsFile):
        """Knows how to abort a store transaction."""

    def finishStoreTransaction(fsFile):
        """Knows how to finish a store transaction."""


class IFSStorage(zope.interface.Interface):
    """File system storage which use a path to a file system folder.

        Normaly any storage can use the default IFSFile implementation but it's
        also posssible that a special IFSStorage requires a special IFSFile
        implementation. Or as a more common usecase it's possible to inherit
        from FSFile and use such content types as a fsFileFactory.

        If a storage uses different fsFileFactory types, you can use an explicit
        fsFileFactory as argument in the store method.

        An important part is the storageName value. The storageName get set
        to the returned IFSFile instance after the object is created. This
        allows us to bind an IFSFile to it's relevant storage utility. Note,
        an IFSStorage utility uses registration names which isn't an 1:1
        relation to the used stroageName. A storageName is allways the same even
        if you register the utility more then once within different names.

        The default storageName is an empty string which will fit for unnamed
        utility registration.

        I recommend to use explicit fsFileFactory classes for store different
        content types in one IFSStorage utility and not to create different
        storages with different storageName values for the same storage backend.
        But that's up to you. Just keep in mind the storageName is the used
        IFSStorage utilit name which get used after IFSFile creation. Which
        means the utility must get registered with the used storageName. But
        the storage can also get registered within another additional name.
        Anyway, this is just a side effect because there is no way to get
        an utility name if we lookup an utility because the registry returns
        the utility by it's registry name which the utility itself doesn't know.
        """

    storageName = zope.schema.TextLine(
        title=_(u'Storage Name'),
        description=_(u'Storage name independent from utility name'),
        default=u'',
        required=True)

    readBlockSize = zope.schema.Int(
        title=_(u'File Read Block Size'),
        description=_(u'File Read Block Size'),
        default=32768,
        required=True)

    path = zope.configuration.fields.Path(
        title=_(u'File system storage base path'),
        description=_(u'File system storage base path'),
        required=True,
        constraint=isDirectory,
        max_length=256)

    def remove(fsFile):
        """Remove a given IFSFile from the storage."""

    def getOpenFile(fsFile):
        """Returns an open file based on the given IFSFile or raises NotFound.
        """

    def getFileReader(fsFile):
        """Returns a file reader which is based on the storage read strategy.

        Probably a read adapter will load a file from a storage to the local
        file system or memcache or do anything else before the read adapter
        can support a file iterator and get returned. That's totaly up to the
        read strategy.
        """

    def getStorageDir(fsNameSpace=None):
        """Get the storage directory."""

    # helpers
    def getSize(fsFile):
        """Set meta data based on data dict. Normal only contentType get set.
        """

    def getContentType(fsFile):
        """Get content type for given fsFile."""

    def setMetaData(fsFile, data):
        """Set meta data based on data dict. Normal only contentType get set.
        """


class ITMPFileConsumer(zope.interface.Interface):
    """Support for consume ITMPFile by store method."""

    def store(tmpFile, fileName=None, fsNameSpace=None, fsFileFactory=None):
        """Store a fsFile in the file system based onthe given tmp file.

        This method can store ITMPFile objects in a storage. It returns an
        IFSFile implementation within the required information. The storage is
        able to return the real file based on the given IFSFile instance.
        """


class IFlatPathFSStorage(IFSStorage, IGhostFileSupport,
    IFSStorageTransationSupport):
    """FSPathStorage which stores all files in one single folder.

    Note: Use this storage only if the amount of files will never exceed the
    maximum files which the used file system can store.
    """


class IUserPathFSStorage(IFSStorage, IGhostFileSupport,
    IFSStorageTransationSupport):
    """FSStorage which stores all files in a folder per user.

    This storage relys on the participation. All files for unauthenticated
    users will be stored in a folder called share. All files uploaded from
    authenticated users will be stored in folder named within the principal
    id. Every user folder will be stored in a folder called user,
    """

    sharePath = zope.configuration.fields.Path(
        title=_(u'File system storage share directory path'),
        description=_(u'File system storage share directory path'),
        required=True,
        constraint=isDirectory,
        max_length=256)

    userPath = zope.configuration.fields.Path(
        title=_(u'File system storage user directory path'),
        description=_(u'File system storage user directory path'),
        required=True,
        constraint=isDirectory,
        max_length=256)


class IBushyFSStorage(IFSStorage, IGhostFileSupport,
    IFSStorageTransationSupport):
    """FSPathStorage which stores all files in a bushy directory structure
    based on the objects given key reference oid.

    The storage creates an 8-level directory structure (one level per byte) in
    big-endian order from the oid of an object.
    """

