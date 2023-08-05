======
README
======

This packages provides a file system storage concept based on a delegation
pattern. The package also provides some very simple implementations which
can be used out of the box. The main reason for this package is the need for
a base concept which allows us to implement a front end for MogileFS or other
distributed file system or network storages.

All storages offered from this package do not provide any real database
functionality. They only offer a concept to choose the right storage location
for a given file. This allows us to store uploaded files and read the file
data for download if needed.

A quick overview
----------------

Storage responsibilities:
* write (once)
* storage
* read

The storage implementation is responsible to define how a file gets stored.
Another important part, the storage is responsible how we will read the stored
file data. It should be possible to implement any kind of storage strategies
based on this package. The package itself offers some simple storages which
can store file in a file system as backend. If you use ZEO or RelStorage this
FSStorage can be used if the file system backend is shared by a network based
file system share.

The FSFile implementation provides a simple identifier and a storageName
attribute which allows to lookup the right storage. Every file related
operation on such a file gets delegated to the relevant storage. The IFSFile
implementation is not responsible for this file operations.

The package provides an IFSFileReader adapter, which delegates the read
operation to the named storage utility.

Some sidenotes
--------------

The file operation to storage delegation allows us to implement some very
interesting concepts like:

- storage with built-in virus scanning on file creation based on upload data

- storage with built-in delayed text indexing

- file storage which stores RML source code and converts them to PDF


Write Once Read Many (WORM)
---------------------------

In my point of view, any content management system should never ever replace
file data. If you need to replace file data you should create a new file. Note,
a content management system stores files to download them and manipulate them
on another client. Files on a file system get normally manipulated directly at
the file system level. That's a huge difference. A server doesn't need to
offer file manipulation. If needed, a file can get replaced with a new file.
If absolutely needed, it should be possible to enhance the IFSFile and
FSStorage and provide file data write operations. This base strategy has many
benefits like:

- faster because we never block based on write access

- simpler for versioning

- file ending and content type can never conflict with new upload data

But anyway that's just my point of view.


Ghosts
------

The ghost concept is about *not* delete a stored file immediately.

Some benefits:

- we can keep the file in the file system till we pack our ZODB.

- we can remove ghost files in another transaction and not directly
  if we remove the file. (e.g. because of an open file handle --
  that's a problem on windows)

That means if a file is removed from a storage it becomes a ghost.
Ghosts are still accessible and present in the storage.
You'll have to call ``removeGhostFiles()`` to remove all ghosts.


Implementation notes
--------------------

Some important notes about this implementation:

- the file storage doesn't provide undo. If undo is needed a storage has to
  implement such a logic. This is possible, but not part of this package.

- file handle operations are delegated to the file storage. It's up to the
  storage how and where the file content get stored.

- create or remove a file is observed by a transaction data manager

- FSFile implementation provides WORM by default.

- a storage could provide write often support if needed. But this is not a part
  of this package.


Options
-------

See also the following packages:

- p01.cgi

- p01.tmp

- p01.accelerator

- p01.fswidget

The p01.fswidget package also provides widgets and data converter for z3c.form.


Testing
-------

Now start with the testing setup:

  >>> import os
  >>> from p01.fsfile import interfaces
  >>> from p01.fsfile import storage

We also need a tmp directory:

  >>> import os
  >>> import tempfile
  >>> tmpDir = tempfile.mkdtemp()
  >>> tmpPath = os.path.join(tmpDir, 'tmp')
  >>> flatStoragePath = os.path.join(tmpDir, 'flat')
  >>> bigStoragePath = os.path.join(tmpDir, 'big')
  >>> os.mkdir(tmpPath)
  >>> os.mkdir(flatStoragePath)
  >>> os.mkdir(bigStoragePath)

  >>> tmpPath
  '.../tmp'

  >>> flatStoragePath
  '.../flat'

  >>> bigStoragePath
  '.../big'

Before we can start with IFSFile or IFSStorage testing, we need to provide a
ITMPFile. This tmp file provides some data which we can use for create a
file storage file. Let's create a fake tmp file and use them in our FSFile.

  >>> class TMPFile(object):
  ...     size = 0
  ...     _p_serial = None
  ...     def __init__(self, tmpPath):
  ...         self.tmpPath = tmpPath
  ...         self._file = file(self.tmpPath, 'wb')
  ...         _p_serial = 123
  ...
  ...     def read(self, size=-1):
  ...         return self._file.read(size)
  ...
  ...     def close(self):
  ...         self._file.close()
  ...
  ...     def seek(self, offset, whence=0):
  ...         return self._file.seek(offset, whence)
  ...
  ...     def tell(self):
  ...         if self.closed:
  ...             return 0
  ...         return self._file.tell()
  ...
  ...     def fileno(self):
  ...         return self._file.fileno()
  ...
  ...     def __iter__(self):
  ...         return self._file.__iter__()
  ...
  ...     def write(self, s):
  ...         self.size = len(s)
  ...         return self._file.write(s)
  ...
  ...     def release(self):
  ...         if os.path.exists(self.tmpPath):
  ...             os.remove(self.tmpPath)
  ...
  ...     @property
  ...     def closed(self):
  ...         return self._file.closed

Let's store the tmp file in our tmp directory:

  >>> tmpFilePath = os.path.join(tmpPath, u'tmp.txt')
  >>> tmpFilePath
  u'.../tmp/tmp.txt'

  >>> tmpFile = TMPFile(tmpFilePath)

As you can see, we created a tmp file in our storage:

  >>> os.listdir(tmpPath)
  ['tmp.txt']

Let's write some content to our tmp file:

  >>> tmpFile.write('Obama 08')
  >>> tmpFile.close()


FlatPathFSStorage
-----------------

The FlatPathFSStorage uses a base path, which points to a file system directory
and stores the files in this directory with a flat file structure.

  >>> from ZODB.tests import util
  >>> import transaction

  >>> flatStorage = storage.FlatPathFSStorage(flatStoragePath)
  >>> flatStorage
  <FlatPathFSStorage u'' at u'.../flat'>

  >>> interfaces.IFSStorage.providedBy(flatStorage)
  True

  >>> interfaces.IFlatPathFSStorage.providedBy(flatStorage)
  True

Since our test depends on the ZODB _p_oid argument, we need to setup DB and
commit our storage to this DB:

  >>> db = util.DB()
  >>> conn = db.open()
  >>> conn.root()['Application'] = flatStorage
  >>> transaction.commit()

And provide the utility:

  >>> import zope.component
  >>> zope.component.provideUtility(flatStorage,
  ...     provides=interfaces.IFlatPathFSStorage, name=flatStorage.storageName)

Our storage path should point to the ``flat`` directory located in our tmp
dir.

  >>> flatStorage.path
  u'.../flat'

The storage defines a IFSFile factory:

  >>> flatStorage.fsFileFactory
  <class 'p01.fsfile.file.FSFile'>


store
~~~~~

The storage can store our tmp file which will return a IFSFile instance based
on the given fsFileFactory:

  >>> fsFile = flatStorage.store(tmpFile, u'upload.txt')
  >>> fsFile
  <FSFile, upload.txt fsID
  u'0x00_0x00_0x00_0x00_0x00_0x00_0x00_0x03-...-...-...-...' in u'' ns u''>

the returned object provides the IFSFile interface:

  >>> interfaces.IFSFile.providedBy(fsFile)
  True

As you can see, we created a file with our given file name and the tmp file getd
removed from the directory. This was done by copy the ``tmp.txt`` file to the
new file path:

  >>> os.listdir(flatStorage.path)
  [u'0x00_0x00_0x00_0x00_0x00_0x00_0x00_0x03-...']

Now let's test our IFSFile implementation. This object only stores some
attributes which are used to identify the real file. In our sample the IFSFile
identifier called ``fsID`` is the real file path. But this doesn't need to be
the case. A IFSFile doesn't have to know about the real file location. Only the
storage is responsible to know about the real file location. And the storage
uses the fsID for store this information:

  >>> fsFile.fsID
  u'0x00_0x00_0x00_0x00_0x00_0x00_0x00_0x03-...'


When we don't give it a name it will choose one itself:

  >>> tmpFile2 = TMPFile(os.path.join(tmpPath, u'tmp2.txt'))
  >>> tmpFile2.write('foobar')
  >>> tmpFile2.close()

  >>> fsFile2 = flatStorage.store(tmpFile2)
  >>> fsFile2
  <FSFile, ... fsID
  u'0x00_0x00_0x00_0x00_0x00_0x00_0x00_0x04-...' in u'' ns u''>

  >>> flatStorage.remove(fsFile2)
  >>> flatStorage.removeGhostFiles()


remove
~~~~~~

Now let's remove our fsFile from the storage. As you know only the storage is
responsible to do so. We can simply call remove with the IFSFile instance as
argument:

  >>> flatStorage.remove(fsFile)

Check if our storage directory is empty now:

  >>> os.listdir(flatStorage.path)
  [u'0x00_0x00_0x00_0x00_0x00_0x00_0x00_0x03-...']

Oh my, the file didn't get removed. You know why? Sure you do. We only added a
ghost file instead of remove the real file from the file system. We can simply
call removeGhostFiles which will remove all real files which are marked as
ghost files.

  >>> flatStorage.removeGhostFiles()

Now you can see calling removeGhostFiles will remove the file:

  >>> os.listdir(flatStorage.path)
  []


BushyFSStorage
--------------

The BushyFSStorage uses a base path which points to a file system directory
and stores the files in a bushy folder layout structure. Since our test depends
on the ZODB _p_oid argument, we need to setup DB and commit our storage to
this DB:

  >>> bigStorage = storage.BushyFSStorage(bigStoragePath)

  >>> conn.root()['Application'] = bigStorage
  >>> transaction.commit()

  >>> zope.component.provideUtility(bigStorage,
  ...     provides=interfaces.IFlatPathFSStorage, name=bigStorage.storageName)


  >>> bigStorage
  <BushyFSStorage u'' at u'.../big'>

  >>> interfaces.IFSStorage.providedBy(bigStorage)
  True

  >>> interfaces.IBushyFSStorage.providedBy(bigStorage)
  True

Our storage path should point to the ``big`` directory located in our tmp dir.

  >>> bigStorage.path
  u'.../big'

The storage defines a IFSFile factory:

  >>> flatStorage.fsFileFactory
  <class 'p01.fsfile.file.FSFile'>


store
~~~~~

Let's setup a new tmp file for test our storage:

  >>> tmpFilePath = os.path.join(tmpPath, u'tmp.txt')
  >>> tmpFile = TMPFile(tmpFilePath)
  >>> tmpFile.write('Obama 12')
  >>> tmpFile.close()

  >>> fsFile = bigStorage.store(tmpFile, u'upload.txt')
  >>> fsFile
  <FSFile, upload.txt fsID
  u'0x00/0x00/0x00/0x00/0x00/0x00/0x00/0x07/...-...-...-...' in u'' ns u''>

the returned object provides the IFSFile interface:

  >>> interfaces.IFSFile.providedBy(fsFile)
  True

Now let's test our IFSFile implementation. The IFSFile only stores some
attributes which are used for identify the real file. In our sample the IFSFile
identifier called ``fsID`` is the real file path.

  >>> fsFile.fsID
  u'0x00/0x00/0x00/0x00/0x00/0x00/0x00/0x07/...-...-...-...'

  >>> os.path.exists(fsFile.path)
  True


remove
~~~~~~

Now let's remove our fsFile from the storage. As you know only the storage is
responsible for do so. We can simply call remove with the IFSFile instance as
argument:

  >>> bigStorage.remove(fsFile)

Check if our storage directory is empty now:

  >>> path = os.path.split(fsFile.path)[0]
  >>> os.listdir(path)
  [u'...-...-...-...']

Oh my, the file didn't get removed. You know why? Sure you do. We only added a
ghost file instead of remove the real file from the file system. We can simply
call removeGhostFiles which will remove all real files which are marked as
ghost files.

  >>> bigStorage.removeGhostFiles()

Now you can see calling removeGhostFiles will remove the file:

  >>> os.listdir(path)
  []


getFileReader
-------------

We can get an IFSFileReader adapter from a storage. This file reader adapter
provides IResult and can be used as direct download wrapper. But first we need
to register our IFSFileReader adapter:

  >>> import zope.component
  >>> from p01.fsfile.file import FSFileReader
  >>> from p01.fsfile.file import getFileReader
  >>> zope.component.provideAdapter(FSFileReader)
  >>> zope.component.provideAdapter(getFileReader)

  >>> bigStorage.getFileReader(fsFile)
  Traceback (most recent call last):
  ...
  NotFound: Object: <BushyFSStorage u'' at u'...'>,
  name: u'0x00/0x00/0x00/0x00/0x00/0x00/0x00/0x07/...-...-...-...'

Of course we didn't find the file we removed above, let's create a new file:

  >>> zope.component.provideUtility(flatStorage, interfaces.IFSStorage,
  ...     name=flatStorage.storageName)

  >>> tmpFilePath = os.path.abspath(os.path.join(flatStoragePath, u'tmp2.txt'))
  >>> tmpFile = TMPFile(tmpFilePath)
  >>> tmpFile.write('New file')
  >>> tmpFile.close()
  >>> fsFile = flatStorage.store(tmpFile, u'new.txt')

Now try again to get the file reader from storage:

  >>> firstFileReader = flatStorage.getFileReader(fsFile)
  >>> firstFileReader
  <FSFileReader
  for u'0x00_0x00_0x00_0x00_0x00_0x00_0x00_0x08-...' from u''>

We also can adapt IFSFileReader directly to the IFSFile:

  >>> secondFileReader = interfaces.IFSFileReader(fsFile)
  >>> secondFileReader
  <FSFileReader
  for u'0x00_0x00_0x00_0x00_0x00_0x00_0x00_0x08-...' from u''>

Reading from both readers should give the equivalent result:

  >>> print firstFileReader.read()
  New file

  >>> firstFileReader._closed
  True

Read from the second with __iter__:

  >>> for i in secondFileReader:
  ...     print i
  New file

  >>> secondFileReader._closed
  True

Now remove the fs file. This will mark the fsFile as a ghost file because there
are still open file handles. This operation doesn't remove the file itself.
We still point ot the fsID path:

  >>> os.path.exists(fsFile.path)
  True

  >>> flatStorage.remove(fsFile)
  >>> fsFile.isGhost
  True

  >>> os.path.exists(fsFile.path)
  True

Now check if the file reader still will get the file from our file system:

  >>> newReader = flatStorage.getFileReader(fsFile)
  Traceback (most recent call last):
  ...
  NotFound: Object: <FlatPathFSStorage u'' at u'.../flat'>,
  name: u'0x00_0x00_0x00_0x00_0x00_0x00_0x00_0x08-...-...-...-...'

After we reomve the ghost files, the fsID path from our fsFile is gone:

  >>> flatStorage.removeGhostFiles()

  >>> os.path.exists(fsFile.fsID)
  False

And our flat storage is empty again:

  >>> os.listdir(flatStorage.path)
  []

Now check if all other directories are empty:

  >>> os.listdir(tmpPath)
  []

  >>> os.listdir(flatStoragePath)
  []

  >>> os.listdir(tmpDir)
  ['big', 'flat', 'tmp']

Close all readers anyway:

  >>> firstFileReader.close()

Trying to get the reader again (after the file is removed) still does not work:

  >>> newReader = flatStorage.getFileReader(fsFile)
  Traceback (most recent call last):
  ...
  NotFound: Object: <FlatPathFSStorage u'' at u'.../flat'>,
  name: u'0x00_0x00_0x00_0x00_0x00_0x00_0x00_0x08-...-...-...-...'


And cleanup our directories:

  >>> import shutil
  >>> shutil.rmtree(tmpDir)

  >>> os.path.exists(tmpDir)
  False
