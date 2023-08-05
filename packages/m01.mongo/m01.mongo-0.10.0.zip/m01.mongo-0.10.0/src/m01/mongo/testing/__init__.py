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

import os
import unittest

import zope.interface
import zope.schema
import zope.location.interfaces
from zope.securitypolicy.interfaces import IGrantInfo
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from zope.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.securitypolicy.interfaces import IRolePermissionManager

import m01.stub.testing

import m01.mongo
import m01.mongo.schema
from m01.mongo import interfaces
from m01.mongo import base
from m01.mongo import item
from m01.mongo import storage
from m01.mongo import container
from m01.mongo import security
from m01.mongo import pool
from m01.mongo.fieldproperty import MongoFieldProperty
from m01.mongo.fieldproperty import MongoDateProperty
from m01.mongo.fieldproperty import MongoGeoLocationProperty
from m01.mongo.fieldproperty import MongoObjectProperty


# mongo db name used for testing
TEST_DB_NAME = 'm01_mongo_testing'


###############################################################################
#
# test helper methods (moved to m01.mongofake)
#
###############################################################################

from m01.mongofake import pprint
from m01.mongofake import RENormalizer
from m01.mongofake import reNormalizer


###############################################################################
#
# fake MongoDB connection pool (moved to m01.mongofake)
#
###############################################################################

from m01.mongofake import FakeDatabase
from m01.mongofake import FakeMongoConnection
# single shared connection instance
from m01.mongofake import fakeMongoConnection

from m01.mongofake import FakeMongoConnectionPool
# single shared connection pool instance
from m01.mongofake import fakeMongoConnectionPool


###############################################################################
#
# TestCase
#
###############################################################################

class TestCase(unittest.TestCase):

    iface = None
    klass = None

    def getTestInterface(self):
        if self.iface is not None:
            return self.iface
        msg = 'Subclasses has to implement getTestInterface()'
        raise NotImplementedError, msg

    def getTestClass(self):
        if self.klass is not None:
            return self.klass
        raise NotImplementedError, 'Subclasses has to implement getTestClass()'

    def getTestData(self):
        return {}

    def makeTestObject(self, data=None):
        # provide default positional or keyword arguments
        if data is None:
            data = self.getTestData()
        testclass = self.getTestClass()
        return testclass(data)


# TODO: implement something like this for test integration
#class MongoIntegrationTestMixin(object):
#    """Mongo integraton test mixin class"""
#
#    def getDumpData(self):
#        return {}
#
#    def test_default_values(self):
#        # integration test
#        obj = self.makeTestObject()
#        schema = self.getTestInterface()
#        fields = zope.schema.getFields(schema)
#        for name, field in fields.items():
#            if field.default != getattr(obj, name):
#                msg = "field %s default %s not equal value %s" %(
#                    name, field.default, getattr(obj, name))
#                raise AssertionError(msg)
#
#    def test_data_integration(self):
#        # integration test
#        obj = self.makeTestObject()
#        dumpData = self.getDumpData()
#        dump = obj.dump()
#        self.assert_(dumpData, dump)


###############################################################################
#
# Public Base Tests
#
###############################################################################

from zope.interface.verify import verifyObject
from zope.interface.verify import verifyClass


class MongoItemBaseTest(TestCase):
    """MongoItem base test"""

    def test_verifyClass(self):
        # class test
        self.assert_(verifyClass(self.getTestInterface(), self.getTestClass()))

    def test_verifyObject(self):
        # object test
        self.assert_(verifyObject(self.getTestInterface(),
            self.makeTestObject()))

    def test_providedBy_IMongoItem(self):
        obj = self.makeTestObject()
        self.assert_(interfaces.IMongoItem.providedBy(obj), True)

    def test_mongo_id(self):
        obj = self.makeTestObject()
        self.assertNotEqual(obj._id, None)

    def test_name(self):
        obj = self.makeTestObject()
        self.assertNotEqual(obj.__name__, None)


class MongoObjectBaseTest(TestCase):
    """MongoItem base test"""

    def test_verifyClass(self):
        # class test
        self.assert_(verifyClass(self.getTestInterface(), self.getTestClass()))

    def test_verifyObject(self):
        # object test
        self.assert_(verifyObject(self.getTestInterface(),
            self.makeTestObject()))

    def test_providedBy_IMongoObject(self):
        obj = self.makeTestObject()
        self.assert_(interfaces.IMongoObject.providedBy(obj), True)

    def test_mongo_id(self):
        obj = self.makeTestObject()
        self.assertNotEqual(obj._id, None)

    def test_name(self):
        obj = self.makeTestObject()
        self.assertNotEqual(obj.__name__, None)


class MongoSubItemBaseTest(TestCase):
    """MongoSubItem base test"""

    def test_verifyClass(self):
        # class test
        self.assert_(verifyClass(self.getTestInterface(), self.getTestClass()))

    def test_verifyObject(self):
        # object test
        self.assert_(verifyObject(self.getTestInterface(),
            self.makeTestObject()))

    def test_providedBy_IMongoSubItem(self):
        obj = self.makeTestObject()
        self.assert_(interfaces.IMongoSubItem.providedBy(obj), True)

    def test_mongo_id(self):
        obj = self.makeTestObject()
        self.assertNotEqual(obj._id, None)

    def test_name(self):
        obj = self.makeTestObject()
        self.assertNotEqual(obj.__name__, None)


class MongoContainerBaseTest(TestCase):
    """MongoContainer base test"""

    def test_verifyClass(self):
        # class test
        self.assert_(verifyClass(self.getTestInterface(), self.getTestClass()))

    def test_verifyObject(self):
        # object test
        self.assert_(verifyObject(self.getTestInterface(),
            self.makeTestObject()))

    def test_providedBy_IMongoContainer(self):
        obj = self.makeTestObject()
        self.assert_(interfaces.IMongoContainer.providedBy(obj), True)


class MongoStorageBaseTest(TestCase):
    """MongoStorage base test"""

    def test_verifyClass(self):
        # class test
        self.assert_(verifyClass(self.getTestInterface(), self.getTestClass()))

    def test_verifyObject(self):
        # object test
        self.assert_(verifyObject(self.getTestInterface(),
            self.makeTestObject()))

    def test_providedBy_IMongoStorage(self):
        obj = self.makeTestObject()
        self.assert_(interfaces.IMongoStorage.providedBy(obj), True)


##############################################################################
#
# test setup methods
#
##############################################################################

_testConnection = None

def getTestConnection():
    return _testConnection

def getTestDatabase():
    global _testConnection
    return _testConnection[TEST_DB_NAME]

def dropTestDatabase():
    if _testConnection is not None:
        _testConnection.drop_database(TEST_DB_NAME)

# mongodb connection setup
def setUpMongoConnection(test=None, host='localhost', port=45017):
    """Patch _mongoConnectionPoolFactory in MongoStorage."""
    global _testConnection
    p = pool.MongoConnectionPool(host, port)
    _testConnection = p.connection

def tearDownMongoConnection(test=None):
    global _testConnection
    dropTestDatabase()
    _testConnection = None


# fake mongodb setup
def setUpFakeMongoDB(test=None):
    """Patch _mongoConnectionPoolFactory in MongoStorage."""
    global _testConnection
    _testConnection = fakeMongoConnection

def tearDownFakeMongoDB(test=None):
    global _testConnection
    dropTestDatabase()
    _testConnection = None


# stub mongodb server
def setUpMongoDBHook():
    def getMongoDBStubSetUp(test):
        host = 'localhost'
        port = 45020
        # lazy test setup
        here = os.path.dirname(__file__)
        sandBoxDir = os.path.join(here, 'sandbox')
        m01.stub.testing.startMongoDBServer(host, port, sandBoxDir=sandBoxDir)
        p = pool.MongoConnectionPool(host, port)
        global _testConnection
        _testConnection = p.connection
    return getMongoDBStubSetUp

setUpStubMongoDB = setUpMongoDBHook()

def tearDownMongoDBHook(sleep=0.5):
    def getMongoDBStubTearDown(test):
        # lazy test tear down
        m01.stub.testing.stopMongoDBServer(sleep)
        global _testConnection
        _testConnection = None
    return getMongoDBStubTearDown

tearDownStubMongoDB = tearDownMongoDBHook()

class TestCollectionMixin(object):
    """Fake test collection mixin class"""

    @property
    def collection(self):
        db = getTestDatabase()
        return db['test']
#
#def getTestCollection(collectionName='test'):
#    p = pool.MongoConnectionPool('localhost', 27017)
#    connection = p.connection
#    db = connection['testing']
#    return db[collectionName]
#
#
#class TestCollectionMixin(object):
#    """Test collection mixin class"""
#
#    @property
#    def collection(self):
#        return getTestCollection()
#
#
#def getFakeTestCollection(collectionName='test'):
#    db = _testConnection[TEST_DB_NAME]
#    return db[collectionName]

##############################################################################
#
# test setup helper
#
##############################################################################

# security policy testing setup
def setUpSecurityPolicyAdapters():
    zope.component.provideAdapter(security.PrincipalPermissionManager,
        (interfaces.ISecurityAware,), IPrincipalPermissionManager)
    zope.component.provideAdapter(security.PrincipalRoleManager,
        (interfaces.ISecurityAware,), IPrincipalRoleManager)
    zope.component.provideAdapter(security.RolePermissionManager,
        (interfaces.ISecurityAware,), IRolePermissionManager)
    zope.component.provideAdapter(security.GrantInfoAdapter,
        (interfaces.ISecurityAware,), IGrantInfo)


##############################################################################
#
# test components
#
##############################################################################

# MongoSubItem
class ISampleSubItem(interfaces.IMongoSubItem):
    """Sample sub item interface."""

    text = zope.schema.TextLine(
        title=u'Text',
        description=u'Text',
        default=u'',
        required=True)


class SampleSubItem(item.MongoSubItem):
    """Sample sub item."""

    zope.interface.implements(ISampleSubItem)

    dumpNames = ['text']

    text = MongoFieldProperty(ISampleSubItem['text'])


# test schema for MongoItem with sub item
class ITestSchema(zope.interface.Interface):
    """Basic sample schema."""

    title = zope.schema.TextLine(
        title=u'Title',
        description=u'Title',
        default=u'',
        required=True)

    description = zope.schema.Text(
        title=u'Description',
        description=u'Description',
        default=u'',
        required=False)

    item = zope.schema.Object(
        title=u'Mongo Item',
        description=u'Mongo Item',
        schema=ISampleSubItem,
        default=None,
        required=False,
        )

    number = zope.schema.Int(
        title=u'Number',
        description=u'Number',
        default=None,
        required=False)

    numbers = m01.mongo.schema.MongoList(
        title=u'Numbers',
        description=u'Numbers',
        value_type=zope.schema.Int(
            title=u'Number',
            description=u'Number',
            ),
        default=[],
        required=False)

    comments = m01.mongo.schema.MongoList(
        title=u'Comments',
        description=u'Comments',
        value_type=zope.schema.Object(
            title=u'Comment',
            description=u'Comment',
            schema=ISampleSubItem,
            default=None,
            required=False,
            ),
        default=[],
        required=False)

    date = m01.mongo.schema.MongoDate(
        title=u'Date',
        description=u'Date',
        required=False)


# MongoStorage
class ISampleStorageItem(ITestSchema, interfaces.IMongoStorageItem):
    """Sample item interface."""

    __name__ = zope.schema.TextLine(
        title=u'Title',
        description=u'Title',
        missing_value=u'',
        default=None,
        required=True)


class SampleStorageItem(item.MongoStorageItem, base.MongoUpdateMixin):
    """Sample item."""

    zope.interface.implements(ISampleStorageItem)

    title = MongoFieldProperty(ISampleStorageItem['title'])
    description = MongoFieldProperty(ISampleStorageItem['description'])
    item = MongoFieldProperty(ISampleStorageItem['item'])
    number = MongoFieldProperty(ISampleStorageItem['number'])
    numbers = MongoFieldProperty(ISampleStorageItem['numbers'])
    comments = MongoFieldProperty(ISampleStorageItem['comments'])
    date = MongoDateProperty(ISampleStorageItem['date'])

    dumpNames = ['title', 'description', 'item',  'numbers', 'number',
                 'comments', 'date']

    converters = {'item': SampleSubItem,
                  'comments': SampleSubItem}


class ISampleStorage(interfaces.IMongoStorage):
    """Sample storage interface."""


class SampleStorage(TestCollectionMixin, storage.MongoStorage):
    """Sample storage."""

    zope.interface.implements(ISampleStorage)

    def __init__(self):
        pass

    def load(self, data):
        """Load data into the right mongo item."""
        return SampleStorageItem(data)


# MongoContainer
class ISampleContainerItem(ITestSchema, interfaces.IMongoContainerItem,
    zope.location.interfaces.ILocation):
    """Sample item interface."""

    __name__ = zope.schema.TextLine(
        title=u'Title',
        description=u'Title',
        missing_value=u'',
        default=None,
        required=True)


class SampleContainerItem(item.MongoContainerItem):
    """Sample item."""

    zope.interface.implements(ISampleContainerItem)

    __name__ = MongoFieldProperty(ISampleContainerItem['__name__'])
    title = MongoFieldProperty(ISampleContainerItem['title'])
    description = MongoFieldProperty(ISampleContainerItem['description'])
    item = MongoFieldProperty(ISampleContainerItem['item'])
    number = MongoFieldProperty(ISampleContainerItem['number'])
    numbers = MongoFieldProperty(ISampleContainerItem['numbers'])
    comments = MongoFieldProperty(ISampleContainerItem['comments'])
    date = MongoDateProperty(ISampleContainerItem['date'])

    dumpNames = ['title', 'description', 'item',  'numbers', 'number',
                 'comments', 'date']

    converters = {'item': SampleSubItem,
                  'comments': SampleSubItem}


class ISampleContainer(interfaces.IMongoContainer):
    """Sample container interface."""


class SampleContainer(TestCollectionMixin, container.MongoContainer):
    """Sample container."""

    zope.interface.implements(ISampleContainer)

    def load(self, data):
        """Load data into the right mongo item."""
        return SampleContainerItem(data)


# MongoObject
class ISampleMongoObject(ITestSchema, interfaces.IMongoObject):
    """Sample mongo object interface."""


class SampleMongoObject(item.MongoObject):
    """Sample mongo object."""

    zope.interface.implements(ISampleMongoObject)

    title = MongoFieldProperty(ISampleMongoObject['title'])
    description = MongoFieldProperty(ISampleMongoObject['description'])
    item = MongoFieldProperty(ISampleMongoObject['item'])
    number = MongoFieldProperty(ISampleMongoObject['number'])
    numbers = MongoFieldProperty(ISampleMongoObject['numbers'])
    comments = MongoFieldProperty(ISampleMongoObject['comments'])
    date = MongoDateProperty(ISampleMongoObject['date'])

    dumpNames = ['title', 'description', 'item',  'numbers', 'number',
                 'comments', 'date']

    converters = {'item': SampleSubItem,
                  'comments': SampleSubItem}

    @classmethod
    def getCollection(cls, parent):
        conn = fakeMongoConnection
        return conn['m01MongoTesting']['m01MongoObjectTest']


class IContent(zope.interface.Interface):
    """Sample content interface."""

    _moid = zope.schema.Int(
        title=u'Object ID',
        )

    obj = zope.schema.Object(
        title=u'Mongo Object',
        schema=ISampleMongoObject,
        )

class Content(object):
    """Sample content (could be a zope persistent object)."""

    _m_initialized = None

    # could but must not be a zope persistent property
    _moid = zope.schema.fieldproperty.FieldProperty(IContent['_moid'])

    # mongo object property
    obj = MongoObjectProperty(IContent['obj'], SampleMongoObject)

    def __init__(self, _moid):
        self._moid = _moid
        self._m_initialized = True

    def __repr__(self):
        return u'<%s %s>' % (self.__class__.__name__, self._moid)


###############################################################################
#
# complex company sample data
#
###############################################################################

# collections
def getEmployers():
    db = getTestDatabase()
    return db['employers']

def getCompanies():
    db = getTestDatabase()
    return db['companies']

def getRootItems():
    db = getTestDatabase()
    return db['items']

# document
class IDocument(interfaces.IMongoContainerItem):
    """Sample sub item interface."""

    text = zope.schema.TextLine(
        title=u'Text',
        description=u'Text',
        required=True)

class Document(item.MongoContainerItem):
    """Sample sub item."""

    zope.interface.implements(IDocument)

    dumpNames = ['text']

    text = MongoFieldProperty(IDocument['text'])


# employer
class IEmployer(interfaces.IMongoContainerItem, interfaces.IMongoContainer):
    """Sample container interface."""

    name = zope.schema.TextLine(
        title=u'Name',
        description=u'Name',
        required=True)

class Employer(item.MongoContainerItem, container.MongoContainer):
    """Mongo company item and Employer container"""

    name = MongoFieldProperty(IEmployer['name'])

    dumpNames = ['name']

    @property
    def cacheKey(self):
        return self.__name__

    @property
    def collection(self):
        return getEmployers()

    def load(self, data):
        """Load data into the right mongo item."""
        return Document(data)


# company
class ICompany(interfaces.IMongoContainerItem, interfaces.IMongoContainer):
    """Sample container interface."""

    name = zope.schema.TextLine(
        title=u'Name',
        description=u'Name',
        required=True)

class Company(item.MongoContainerItem, container.MongoContainer):
    """Mongo company item and Employer container"""

    name = MongoFieldProperty(ICompany['name'])

    dumpNames = ['name']

    @property
    def cacheKey(self):
        return self.__name__

    @property
    def collection(self):
        return getEmployers()

    def load(self, data):
        """Load data into the right mongo item."""
        return Employer(data)


# companies
class ICompanies(interfaces.IMongoContainerItem, interfaces.IMongoContainer):
    """Sample container interface."""

    name = zope.schema.TextLine(
        title=u'Name',
        description=u'Name',
        required=True)

class Companies(item.MongoContainerItem, container.MongoContainer):
    """Mongo company container"""

    name = MongoFieldProperty(ICompanies['name'])

    dumpNames = ['name']

    @property
    def cacheKey(self):
        return self.__name__

    @property
    def collection(self):
        return getCompanies()

    def load(self, data):
        """Load data into the right mongo item."""
        return Company(data)


class IGeoSample(interfaces.IMongoContainerItem):
    """Geo sample interface."""

    name = zope.schema.TextLine(
        title=u'Name',
        description=u'Name',
        required=True)

    lonlat = zope.schema.Object(
        title=u'Location',
        description=u'Location',
        schema=interfaces.IGeoLocation,
        required=False)


class GeoSample(item.MongoContainerItem):
    """Geo sample item"""

    zope.interface.implements(IGeoSample)

    name = MongoFieldProperty(IGeoSample['name'])
    lonlat = MongoGeoLocationProperty(IGeoSample['lonlat'])

    dumpNames = ['name', 'lonlat']
