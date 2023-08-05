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

import threading
import logging
import pymongo

import zope.interface

from m01.mongo import interfaces


log = logging.getLogger('m01.mongo')

LOCAL = threading.local()



# TODO: should we implement better autoconnect option with something like this
#import pymongo
#from time import sleep
#
#def reconnect(f):
#    def f_retry(*args, **kwargs):
#        while True:
#            try:
#                return f(*args, **kwargs)
#            except pymongo.errors.AutoReconnect, e:
#                print('Fail to execute %s [%s]' % (f.__name__, e))
#            sleep(0.1)
#    return f_retry



class MongoConnectionPool(object):
    """MongoDB connection pool contains the connection to a mongodb server.
    
    MongoConnectionPool is a global named utility, knows how to setup a
    thread (safe) shared mongodb connection instance.
    
    Note: pymongo offers connection pooling which we do not need since we use
    one connection per thread

    """

    zope.interface.implements(interfaces.IMongoConnectionPool)

    _mongoConnectionFactory = pymongo.Connection

    def __init__(self, host='localhost', port=27017, logLevel=20,
        tz_aware=True, connectionFactory=None):
        self.host = host
        self.port = port
        self.key = 'm01.mongo-%s-%s' %(self.host, self.port)
        self.tz_aware = tz_aware
        if connectionFactory is not None:
            self._mongoConnectionFactory = connectionFactory
        self.logLevel = logLevel

    @property
    def storage(self):
        return LOCAL.__dict__

    def disconnect(self):
        conn = self.storage.get(self.key, None)
        if conn is not None:
            conn.disconnect()
        self.storage[self.key] = None

    @property
    def connection(self):
        conn = self.storage.get(self.key, None)
        if conn is None:
            self.storage[self.key] = conn = self._mongoConnectionFactory(
                self.host, self.port, tz_aware=self.tz_aware)
            if self.logLevel:
                log.log(self.logLevel, "Create connection for %s:%s" % (
                    self.host, self.port))

        return conn
