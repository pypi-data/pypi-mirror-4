###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import transaction
from transaction.interfaces import IDataManager

import zope.interface

from m01.mongo import LOCAL


class MongoTransactionDataManager(object):
    """Transaction Data manager for mongo object.

    The transaction data manager is responsible for add, modify and remove a
    mongo object in a mongo database and will ensure cleanup and error handling.
    
    This transaction manager should be generic since he delegates operations
    to the IMongoStorage.
    """

    zope.interface.implements(IDataManager)

    def __init__(self, obj, tm, transaction):
        self.transaction_manager = tm # useless but defined by interface
        self.transaction = transaction
        self.objects = []
        self.objects.append(obj)
        self._prepared = False

    def append(self, obj):
        if obj not in self.objects:
            self.objects.append(obj)

    def tpc_begin(self, transaction):
        """Begin commit of a transaction, starting the two-phase commit."""
        if self._prepared:
            raise TypeError('Already prepared')
        self._checkTransaction(transaction)
        self._prepared = True
        self.transaction = transaction
        # before we start processing, remove our thread local reference
        delattr(LOCAL, 'MongoTransactionDataManager')
        for obj in self.objects:
            obj.begin()

    def commit(self, transaction):
        """Delegate the commit call to the object."""
        if not self._prepared:
            raise TypeError('Not prepared to commit')
        self._checkTransaction(transaction)
        self.transaction = None
        self._prepared = False
        for obj in self.objects:
            obj.commit()

    def abort(self, transaction):
        """Abort a transaction and forget all changes.
        
        This call get dispatched to tpc_abort since abort get not always called
        if we abort a transaction.
        """
        self.tpc_abort(transaction)

    def tpc_finish(self, transaction):
        """Indicate confirmation that the transaction is done.
        
         This should never fail.
         """
        for obj in self.objects:
            obj.finish()
        # remove objects which will prevent calling this twice
        self.objects = []

    def tpc_vote(self, transaction):
        """Verify that a data manager can commit the transaction."""
        self._checkTransaction(transaction)
        for obj in self.objects:
            obj.vote()

    def tpc_abort(self, transaction):
        """Abort a transaction. This should never fail.
        
        This method can get called more then once because we only abort on the
        first call. This is important if since abort() call can get skipped if
        an error happens before this data manager get commited.
        """
        self._checkTransaction(transaction)
        if self.transaction is not None:
            self.transaction = None
        self._prepared = False
        for obj in self.objects:
            obj.abort()
        # remove objects which will prevent calling this twice
        self.objects = []

    def sortKey(self):
        # use an order key which (hopefully) forces to order as last item.
        # Remember, python orders a list like:
        # [None, 42, time.time(), 123456789123456789L, 'AA', 'BB', 'aa', 'bb']
        return 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'

    # helpers
    def _checkTransaction(self, transaction):
        """Check for a valid transaction."""
        if (self.transaction is not None and
            self.transaction is not transaction):
            raise TypeError("Transaction missmatch", transaction, 
                self.transaction)


def ensureMongoTransaction(obj):
    """Observes a mongo items

    Threading local provides a reference to our shared transaction data manager.
    This will ensure that we never use more then one transaction data manager
    if more the one storage or object get used.
    """
    tm = transaction.manager
    txn = tm.get()
    tdm = getattr(LOCAL, 'MongoTransactionDataManager', None)
    if tdm is None or tdm.transaction != txn:
        tdm = MongoTransactionDataManager(obj, tm, txn)
        setattr(LOCAL, 'MongoTransactionDataManager', tdm)
        txn.join(tdm)
    else:
        tdm.append(obj)
    return tdm
