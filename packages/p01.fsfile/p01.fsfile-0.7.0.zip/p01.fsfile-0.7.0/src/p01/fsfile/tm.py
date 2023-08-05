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

import time
import transaction
from transaction.interfaces import IDataManager

import zope.interface


class FSFileStoreTransactionDataManager(object):
    """Transaction Data manager for store a file in file system storage.

    The transaction data manager is responsible for cleanup and error handling.
    
    This transaction manager should be generic since he delegates to operations
    to the IFSFile implementation relevant IFSStorage.
    """

    zope.interface.implements(IDataManager)

    def __init__(self, fsStorage, fsFile, tm):
        self.fsStorage = fsStorage
        self.fsFile = fsFile
        self.transaction = tm.get()
        self._timeStamp = time.time()
        self._prepared = False

    def tpc_begin(self, transaction):
        """Begin commit of a transaction, starting the two-phase commit."""
        if self._prepared:
            raise TypeError('Already prepared')
        self._checkTransaction(transaction)
        self._prepared = True
        self.transaction = transaction

    def commit(self, transaction):
        """Commit modifications to registered objects."""
        if not self._prepared:
            raise TypeError('Not prepared to commit')
        self._checkTransaction(transaction)
        self.transaction = None
        self._prepared = False
        if self.fsFile is not None and self.fsStorage is not None:
            self.fsStorage.commitStoreTransaction(self.fsFile)

    def abort(self, transaction):
        """Abort a transaction and forget all changes."""
        self.tpc_abort(transaction)

    def tpc_finish(self, transaction):
        """Indicate confirmation that the transaction is done."""
        if self.fsFile is not None and self.fsStorage is not None:
            self.fsStorage.finishStoreTransaction(self.fsFile)

    def tpc_vote(self, transaction):
        """Verify that a data manager can commit the transaction."""
        self._checkTransaction(transaction)
        if self.fsFile is not None and self.fsStorage is not None:
            self.fsStorage.voteStoreTransaction(self.fsFile)

    def tpc_abort(self, transaction):
        """Abort a transaction. This should never fail.
        
        The method can get called more then once because we only abort on the
        first call. This is important if since abort() call can get skipped if
        an error happens before this data manager get commited.
        """
        self._checkTransaction(transaction)
        if self.transaction is not None:
            self.transaction = None
        self._prepared = False
        if self.fsFile is not None and self.fsStorage is not None:
            self.fsStorage.abortStoreTransaction(self.fsFile)
            self.fsStorage = None
            self.fsFile = None

    def sortKey(self):
        return self._timeStamp

    # helpers
    def _checkTransaction(self, transaction):
        """Check for a valid transaction."""
        if (self.transaction is not None and
            self.transaction is not transaction):
            raise TypeError("Transaction missmatch", transaction, 
                self.transaction)
