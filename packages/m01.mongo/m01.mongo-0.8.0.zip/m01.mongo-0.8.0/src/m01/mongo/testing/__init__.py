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

import copy
import datetime
import os
import persistent
import re
import types
import unittest
import pprint as pp

from bson import objectid
from bson import son
from pymongo import cursor

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
# test helper methods
#
###############################################################################


def pprint(data):
    """Can pprint a bson.son.SON instance like a dict"""
    pp.pprint(m01.mongo.dictify(data))


class RENormalizer(object):
    """Normalizer which can convert text based on regex patterns"""

    def __init__(self, patterns):
        self.patterns = patterns
        self.transformers = map(self._cook, patterns)

    def _cook(self, pattern):
        if callable(pattern):
            return pattern
        regexp, replacement = pattern
        return lambda text: regexp.sub(replacement, text)

    def addPattern(self, pattern):
        patterns = list(self.patterns)
        patterns.append(pattern)
        self.transformers = map(self._cook, patterns)
        self.patterns = patterns

    def __call__(self, data):
        """Recursive normalize a SON instance, dict or text"""
        if not isinstance(data, basestring):
            data = pp.pformat(m01.mongo.dictify(data))
        for normalizer in self.transformers:
            data = normalizer(m01.mongo.dictify(data))
        return data

    def pprint(self, data):
        """Pretty print data"""
        if isinstance(data, cursor.Cursor):
            for item in data:
                print self(item)
        else:
            print self(data)


# see testing.txt for a sample usage
reNormalizer = RENormalizer([
   (re.compile(u"(\d\d\d\d)-(\d\d)-(\d\d)[tT](\d\d):(\d\d):(\d\d)"),
               r"NNNN-NN-NNTNN:NN:NN"),
   (re.compile(u"(\d\d\d\d)-(\d\d)-(\d\d) (\d\d):(\d\d):(\d\d)"),
               r"NNNN-NN-NN NN:NN:NN"),
   (re.compile("ObjectId\(\'[a-zA-Z0-9]+\'\)"), r"ObjectId('...')"),
   (re.compile("Timestamp\([a-zA-Z0-9, ]+\)"), r"Timestamp('...')"),
   (re.compile("datetime.datetime\([a-zA-Z0-9, ]+tzinfo=<bson.tz_util.FixedOffset[a-zA-Z0-9 ]+>\)"),
               "datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>)"),
   (re.compile("datetime.datetime\([a-zA-Z0-9, ]+tzinfo=[a-zA-Z0-9>]+\)"),
               "datetime(..., tzinfo= ...)"),
   (re.compile("datetime\([a-z0-9, ]+\)"), "datetime(...)"),
   (re.compile("object at 0x[a-zA-Z0-9]+"), "object at ..."),
   ])


###############################################################################
#
# fake MongoDB connection pool
#
###############################################################################

class OrderedData(object):
    """Ordered data."""

    def __init__(self):
        self.data = {}
        self._order = []

    def __len__(self):
        return len(self.data)

    def __contains__(self, key):
        return key in self.data

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, item):
        if key not in self._order:
            self._order.append(key)
        self.data[key] = copy.deepcopy(item)

    def __delitem__(self, key):
        del self.data[key]
        self._order.remove(key)

    def get(self, key, default=None):
        """Get item by key"""
        return self.data.get(key, default)

    def keys(self):
        return self._order

    def values(self):
        for key in self._order:
            return self.data[key]

    def items(self):
        for key in self._order:
            yield (key, self.data[key])

    def __iter__(self):
        for key in self._order:
            yield self.data[key]

    def __repr__(self):
        return repr(self.data.values())


def sortByAttribute(name, order):
    def sort(d1, d2):
        v1 = d1.get(name, None)
        v2 = d2.get(name, None)
        try:
            res = cmp(v1, v2)
        except TypeError, e:
            res = -1
        if order:
            return res
        else:
            return -res
    return sort

def cursor_comparator(keys):
    def comparator(a, b):
        for k,d in keys:
            part = cmp(a.get(k), b.get(k))
            if part: return part * d
        return 0
    return comparator

NOVALUEMARKER = object()

def getPart(doc, k):
    parts = k.split('.')

    def getP(doc, part):
        try:
            # try an attribute
            return getattr(doc, part)
        except AttributeError:
            try:
                # try a dict
                return doc[part]
            except TypeError:
                try:
                    # try a sequence
                    return doc[int(part)]
                except:
                    pass
        return NOVALUEMARKER

    d = doc
    for p in parts:
        prevD = d
        d = getP(d, p)
        if d == NOVALUEMARKER:
            #if it starts with '$' try again without $, like for $id
            if p.startswith('$'):
                d = getP(prevD, p[1:])
                if d == NOVALUEMARKER:
                    return d
    return d

class FakeCursor(object):
    """Fake cursor."""

    def __init__(self, collection, spec, fields, skip, limit, slave_okay,
                 timeout, tailable, snapshot=False, sort=None,
                 _sock=None, _must_use_master=False):
        # filter and setup docs based on given spec
        self.collection = collection
        self._skip = skip
        self._limit = limit
        self.docs = self._query(collection, spec, sort)
        self.total = len(self.docs)

    def _query(self, collection, spec, sort=None):
        docs = []
        append = docs.append
        for key, doc in collection.docs.items():
            for k, v in spec.items():
                if k in doc and isinstance(v, dict):
                    reject = False
                    for op, value in v.items():
                        if ((op == '$gt' and not doc[k] > value) or
                            (op == '$lt' and not doc[k] < value) or
                            (op == '$gte' and not doc[k] >= value) or
                            (op == '$lte' and not doc[k] <= value) or
                            (op == '$ne' and not doc[k] != value) or
                            (op == '$in' and not doc[k] in value) or
                            (op == '$exists' and not k in doc) or
                            (op == '$all' and not all([vv in doc[k]
                                                       for vv in value])) or
                            (op == '$nin' and not doc[k] not in value)
                            # TODO: $mod, $nor $or, $and, $size, $type, $regex
                            ):
                            reject = True
                            break
                    if reject:
                        break
                else:
                    if '.' in k:
                        # support diving into attributes/documents
                        docVal = getPart(doc, k)
                    else:
                        # Mongo always ignores documents where a key of the
                        # spec is missing.
                        if k not in doc:
                            break
                        docVal = doc.get(k, NOVALUEMARKER)
                    # XXX: This is not generic and will not handle operator
                    # based specs.
                    if docVal != NOVALUEMARKER and v != docVal:
                        break
            else:
                append(copy.deepcopy(doc))

        if sort:
            docs = sorted(docs, cmp=cursor_comparator(sort))

        return docs

    def count(self, with_limit_and_skip=False):
        if with_limit_and_skip:
            return len(self.docs)
        else:
            return self.total

    def skip(self, skip):
        self._skip = skip
        self.docs = self.docs[skip:]
        return self

    def limit(self, limit):
        self._limit = limit
        self.docs = self.docs[:limit]
        return self

    def sort(self, name, order):
        sorter = sortByAttribute(name, order)
        docs = list(self.docs)
        docs.sort(sorter)
        self.docs = docs
        return self

    def __iter__(self):
        return self

    def next(self):
        if len(self.docs):
            next = self.docs.pop(0)
        else:
            raise StopIteration
        return next


class FakeCollection(object):

    def __init__(self, database, name):
        self.database = database
        self.name = name
        self.full_name = '%s.%s' % (database, name)
        self.docs = OrderedData()

    def __getattr__(self, name):
        """Get a sub-collection of this collection by name (e.g. gridfs)"""
        return FakeCollection(self.database, u"%s.%s" % (self.name, name))

    def clear(self):
        for k in self.docs.keys():
            del self.docs[k]

    def count(self):
        return len(self.docs)

    def update(self, spec, document,
               upsert=False, manipulate=False, safe=False, multi=False):
        if not isinstance(spec, types.DictType):
            raise TypeError("spec must be an instance of dict")
        if not isinstance(document, types.DictType):
            raise TypeError("document must be an instance of dict")
        if not isinstance(upsert, types.BooleanType):
            raise TypeError("upsert must be an instance of bool")

        for key, doc in list(self.docs.items()):
            for k, v in spec.items():
                if k in doc and v == doc[k]:
                    setData = document.get('$set')
                    if setData is not None:
                        # do a partial update based on $set data
                        for pk, pv in setData.items():
                            doc[pk] = pv
                    else:
                        self.docs[key] = document
                    break

    def save(self, to_save, manipulate=True, safe=False):
        if not isinstance(to_save, types.DictType):
            raise TypeError("cannot save object of type %s" % type(to_save))

        if "_id" not in to_save:
            return self.insert(to_save, manipulate, safe)
        else:
            self.update({"_id": to_save["_id"]}, to_save, True, manipulate, safe)
            return to_save.get("_id", None)

    def insert(self, doc_or_docs, manipulate=True, safe=False, check_keys=True,
        continue_on_error=True):
        docs = doc_or_docs
        if isinstance(docs, types.DictType):
            docs = [docs]
        for doc in docs:
            oid = doc.get('_id')
            if oid is None:
                oid = objectid.ObjectId()
                doc[u'_id'] = oid
            d = {}
            for k, v in list(doc.items()):
                # use unicode keys as mongodb does
                d[unicode(k)] = v
            self.docs[unicode(oid)] = d

        ids = [doc.get("_id", None) for doc in docs]
        return len(ids) == 1 and ids[0] or ids

    def ensure_index(self, key_or_list, direction=None, unique=False, ttl=300):
        # we do not need indexes
        pass

    def find_one(self, spec_or_object_id=None, fields=None, slave_okay=True,
                 _sock=None, _must_use_master=False):
        spec = spec_or_object_id
        if spec is None:
            spec = son.SON()
        if isinstance(spec, objectid.ObjectId):
            spec = son.SON({"_id": spec})

        for result in self.find(spec, limit=-1, fields=fields,
            slave_okay=slave_okay, _sock=_sock,
            _must_use_master=_must_use_master):
            return result
        return None

    def find(self, spec=None, fields=None, skip=0, limit=0,
             slave_okay=True, timeout=True, snapshot=False, tailable=False,
             sort=None,
             _sock=None, _must_use_master=False):
        if spec is None:
            spec = son.SON()

        if not isinstance(spec, types.DictType):
            raise TypeError("spec must be an instance of dict")
        if not isinstance(fields, (
            types.ListType, types.TupleType, types.NoneType)):
            raise TypeError("fields must be an instance of list or tuple")
        if not isinstance(skip, types.IntType):
            raise TypeError("skip must be an instance of int")
        if not isinstance(limit, types.IntType):
            raise TypeError("limit must be an instance of int")
        if not isinstance(slave_okay, types.BooleanType):
            raise TypeError("slave_okay must be an instance of bool")
        if not isinstance(timeout, types.BooleanType):
            raise TypeError("timeout must be an instance of bool")
        if not isinstance(snapshot, types.BooleanType):
            raise TypeError("snapshot must be an instance of bool")
        if not isinstance(tailable, types.BooleanType):
            raise TypeError("tailable must be an instance of bool")

        if fields is not None:
            if not fields:
                fields = ["_id"]
            fields = self._fields_list_to_dict(fields)

        return FakeCursor(self, spec, fields, skip, limit, slave_okay, timeout,
                      tailable, snapshot, sort=sort, _sock=_sock,
                      _must_use_master=_must_use_master)

    def remove(self, spec_or_object_id, safe=False):
        spec = spec_or_object_id
        if isinstance(spec, objectid.ObjectId):
            spec = son.SON({"_id": spec})

        if not isinstance(spec, types.DictType):
            raise TypeError("spec must be an instance of dict, not %s" %
                            type(spec))

        for doc in self.find(spec_or_object_id, fields=()):
            del self.docs[unicode(doc['_id'])]

    # helper methods
    def _fields_list_to_dict(self, fields):
        as_dict = OrderedData()
        for field in fields:
            if not isinstance(field, types.StringTypes):
                raise TypeError("fields must be a list of key names as "
                                "(string, unicode)")
            as_dict[field] = 1
        return as_dict


class FakeDatabase(object):
    """Fake database."""

    def __init__(self, connection, name):
        self.connection = connection
        self.name = name
        self.cols = {}

    def clear(self):
        for k, col in self.cols.items():
            col.clear()
            del self.cols[k]

    def collection_names(self):
        return list(self.cols.keys())

    def __getattr__(self, name):
        col = self.cols.get(name)
        if col is None:
            col = FakeCollection(self, name)
            self.cols[name] = col
        return col

    def __getitem__(self, name):
        return self.__getattr__(name)

    def create_collection(self, name, **kw):
        return True


class FakeMongoConnection(object):
    """Fake MongoDB connection."""

    def __init__(self):
        self.dbs = {}

    def __call__(self, host='localhost', port=27017, tz_aware=True):
        return self

    def drop_database(self, name):
        db = self.dbs.get(name)
        if db is not None:
            db.clear()
            del self.dbs[name]

    def disconnect(self):
        pass

    def database_names(self):
        return list(self.dbs.keys())

    def __getattr__(self, name):
        db = self.dbs.get(name)
        if db is None:
            db = FakeDatabase(self, name)
            self.dbs[name] = db
        return db

    def __getitem__(self, name):
        return self.__getattr__(name)

# single shared connection instance
fakeMongoConnection = FakeMongoConnection()


class FakeMongoConnectionPool(object):
    """Fake mongodb connection pool."""

    #maybe this is betteR:
    #def __init__(self, host='localhost', port=27017,
    #    connectionFactory=lambda host, port, tz=False: fakeMongoConnection,
    #    logLevel=20):
    #    self.connection = connectionFactory(host, port)

    def __init__(self, host='localhost', port=27017,
        connectionFactory=fakeMongoConnection, logLevel=20):
        self.connection = fakeMongoConnection

    def disconnect(self):
        self.connection.disconnect()

# single shared connection pool instance
fakeMongoConnectionPool = FakeMongoConnectionPool()

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


class SampleStorage(TestCollectionMixin, storage.MongoStorage,
    persistent.Persistent):
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


class SampleContainer(TestCollectionMixin, container.MongoContainer,
    persistent.Persistent):
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

class Content(persistent.Persistent):
    """Sample content."""

    _v_initialized = False

    def __init__(self, _moid):
        self._moid = _moid
        # volatil property not stored in ZODB
        self._v_initialized = True

    @apply
    def _m_initialized():
        def fget(self):
            return self._v_initialized
        def fset(self, value):
            self._v_initialized = value
        return property(fget, fset)

    _moid = zope.schema.fieldproperty.FieldProperty(IContent['_moid'])
    obj = MongoObjectProperty(IContent['obj'], SampleMongoObject)

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
