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

import zope.interface
from zope.container import contained

from m01.mongo import base
from m01.mongo import interfaces


class MongoStorage(base.MongoStorageBase, contained.Contained):
    """Persistent mongo item storage with thread save transaction and caching
    support.
    
    This class can be used without the ZODB.

    Note: don't forget to mixin persistent in your MongoContainer class
    if you like to store such MongoContainer in ZODB.

    """

    zope.interface.implements(interfaces.IMongoStorage)


#class SharedMongoStorage(base.SharedMongoStorageBase, contained.Contained):
#    """Persistent shared mongo item storage with thread save transaction and
#    caching support.
#
#    This implementation uses a shared collection with a namespace for group
#    items.
#    
#    This class can be used without the ZODB.
#
#    Note: don't forget to mixin persistent in your MongoContainer class
#    if you like to store such MongoContainer in ZODB.
#
#    """
#
#    zope.interface.implements(interfaces.ISharedMongoStorage)
