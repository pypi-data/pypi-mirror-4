======
README
======

IMPORTANT:
If you run the tests with the --all option a real mongodb stub server will
start at port 45017!

This package provides non persistent MongoDB object implementations. They can
simply get mixed with persistent.Persistent and contained.Contained if you like
to use them in a mixed MongoDB/ZODB application setup. We currently use this
framework as ORM (object relation mapper) where we map MongoDB objects
to python/zope schema based objects including validation etc.

In our last project, we started with a mixed ZODB/MongoDB application where we
mixed persistent.persistent into IMongoContainer objects. But later we where
so exited about the performance and stability that we removed the ZODB
persistence layer at all. Now we use a ZODB less setup in our application
where we start with a non persistent item as our application root. All required
tools where we use for such a ZODB less application setup are located in the
m01.publisher and p01.recipe.setup package.

NOTE: Some of this test use a fake mongodb located in m01/mongo/testing and some
other tests will use our mongdb stub from the m01.stub package. You can run
the tests with the --all option if you like to run the full tests which will
start and stop the mongodb stub server.

NOTE:
All mongo item interfaces will not provide ILocation or IContained but the
bass mongo item implementations will implement Location which provides the
ILocation interface directly. This makes it simpler for permission
declaration in ZCML.


Testing
-------

  >>> import zope.component
  >>> from m01.mongo import interfaces
  >>> from m01.mongo import getMongoDBConnection
  >>> from m01.mongo.pool import MongoConnectionPool


MongoConnectionPool
--------------------

We need to setup a mongo connection pool. We can do this with a global utility
configuration. Note we use a different port with our stub server setup:

  >>> mongoConnectionPool = MongoConnectionPool('localhost', 45020)
  >>> zope.component.provideUtility(mongoConnectionPool,
  ...     interfaces.IMongoConnectionPool, name='m01.mongo.testing')

The connection pool stores the connection in threading local.


MongoClient
-----------

Now we are able to get a connection pool:

  >>> pool = zope.component.getUtility(interfaces.IMongoConnectionPool,
  ...    name='m01.mongo.testing')

Such a pool knows the connection which is observed by thread local:

  >>> conn1 = pool.connection
  >>> conn1
  MongoClient('localhost', 45020)

We can also use the getMongoDBConnection which knows how to get a connection:

  >>> conn = getMongoDBConnection('m01.mongo.testing')
  >>> conn
  MongoClient('localhost', 45020)

As you can see the connection is able to access the database:

  >>> db = conn.m01MongoTesting
  >>> db
  Database(MongoClient('localhost', 45020), u'm01MongoTesting')

A data base can retrun a collection:

  >>> collection = db['m01MongoTest']
  >>> collection
  Collection(Database(MongoClient('localhost', 45020), u'm01MongoTesting'), u'm01MongoTest')

As you can see we can write to the collection:

  >>> collection.update({'_id': '123'}, {'$inc': {'counter': 1}}, upsert=True)
  {u'updatedExisting': False, u'connectionId': 2, u'ok': 1.0, u'err': None, u'n': 1}

And we can read from the collection:

  >>> collection.find_one({'_id': '123'})
  {u'_id': u'123', u'counter': 1}

Remove the result from our test collection:

  >>> collection.remove({'_id': '123'})
  {u'connectionId': 2, u'ok': 1.0, u'err': None, u'n': 1}


issues
------

The following concept brings mongodb to crash in one of our projects. Just try
to reproduce it here. but it seems to work as it should:

  >>> import datetime
  >>> import bson.son
  >>> import bson.objectid
  >>> import m01.mongo
  >>> from m01.mongo import UTC
  >>> def createAnswer():
  ...     _id = bson.objectid.ObjectId()
  ...     return {'_id': _id,
  ...             '_type': u'DiscussionAnswer',
  ...             'comment': u"I don't know",
  ...             'created': datetime.datetime(2012, 5, 25, 2, 8, 13, 253000, tzinfo=UTC),
  ...             'fullName': u'Alannis Brauer',
  ...             'nickName': 'alannis.brauer',
  ...             'pid': u'4fbee89d7a933127cc0017b2',
  ...             'text': u'Let me google that for you http://lmgtfy.com/?q=what+is+xeebo'}

  >>> def createQuestion(idx):
  ...     _id = m01.mongo.getObjectId(idx)
  ...     a1 = createAnswer()
  ...     a2 = createAnswer()
  ...     return {'__name__': unicode(_id),
  ...             '_id': _id,
  ...             '_type': u'DiscussionQuestion',
  ...             '_version': 1,
  ...             'answers': [
  ...                 bson.son.SON(a1),
  ...                 bson.son.SON(a2)
  ...             ],
  ...             'changed': True,
  ...             'country': u'CHE',
  ...             'created': datetime.datetime(2012, 5, 25, 2, 8, 13, 252000, tzinfo=UTC),
  ...             'description': u'I like to ask the following question: What is xeebo',
  ...             'fullName': u'Emily EMILY',
  ...             'language': u'en',
  ...             'modified': datetime.datetime(2012, 5, 25, 2, 10, 7, 863000, tzinfo=UTC),
  ...             'nickName': 'emily.emily',
  ...             'pid': u'4fbee8a07a933127cc002bd4',
  ...             'removed': False,
  ...             'title': u'What is xeebo',
  ...             'topicNames': ['admin', 'xeebo'],
  ...         }

  >>> idx = 0
  >>> data = []
  >>> for i in range(300):
  ...     qData = createQuestion(idx)
  ...     data.append(bson.son.SON(qData))
  ...     idx += 1

  >>> manipulate = False
  >>> safe = False
  >>> check_keys = True
  >>> res = collection.insert(data, manipulate, safe, check_keys)

  >>> key = unicode(data[0]['__name__'])
  >>> key
  u'000000000000000000000000'

  >>> res = collection.find_one({'__name__': key})
  >>> m01.mongo.testing.reNormalizer.pprint(res)
  {u'__name__': u'000000000000000000000000',
   u'_id': ObjectId('...'),
   u'_type': u'DiscussionQuestion',
   u'_version': 1,
   u'answers': [{u'_id': ObjectId('...'),
                 u'_type': u'DiscussionAnswer',
                 u'comment': u"I don't know",
                 u'created': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
                 u'fullName': u'Alannis Brauer',
                 u'nickName': u'alannis.brauer',
                 u'pid': u'4fbee89d7a933127cc0017b2',
                 u'text': u'Let me google that for you http://lmgtfy.com/?q=what+is+xeebo'},
                {u'_id': ObjectId('...'),
                 u'_type': u'DiscussionAnswer',
                 u'comment': u"I don't know",
                 u'created': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
                 u'fullName': u'Alannis Brauer',
                 u'nickName': u'alannis.brauer',
                 u'pid': u'4fbee89d7a933127cc0017b2',
                 u'text': u'Let me google that for you http://lmgtfy.com/?q=what+is+xeebo'}],
   u'changed': True,
   u'country': u'CHE',
   u'created': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'description': u'I like to ask the following question: What is xeebo',
   u'fullName': u'Emily EMILY',
   u'language': u'en',
   u'modified': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'nickName': u'emily.emily',
   u'pid': u'4fbee8a07a933127cc002bd4',
   u'removed': False,
   u'title': u'What is xeebo',
   u'topicNames': [u'admin', u'xeebo']}

  >>> collection.remove({'__name__': key})
  {u'connectionId': 2, u'ok': 1.0, u'err': None, u'n': 1}


tear down
---------

Now tear down our MongoDB database with our current MongoDB connection:

  >>> import time
  >>> time.sleep(1)
  >>> conn.drop_database('m01MongoTesting')
