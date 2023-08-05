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

from m01.mongo import interfaces
from m01.mongo import base


class MongoContainer(base.MongoContainerBase, contained.Contained):
    """Mongo storage based container supporting item with __name__.
    
    This class can be used without the ZODB.

    Note: don't forget to mixin persistent in your MongoContainer class
    if you like to store such MongoContainer in ZODB.
    """

    zope.interface.implements(interfaces.IMongoContainer)


#class SharedMongoContainer(base.SharedMongoContainerBase, contained.Contained):
#    """Mongo container with shared collection using a namespace for group items.
#    
#    This class can be used without the ZODB.
#
#    Note: don't forget to mixin persistent in your MongoContainer class
#    if you like to store such MongoContainer in ZODB.
#    """
#
#    zope.interface.implements(interfaces.ISharedMongoContainer)
