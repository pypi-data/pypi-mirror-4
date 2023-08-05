===============
Session concept
===============

NOTE: This test will download, setup and start a mongodb server at port 45017!

This package provides a mongodb based session handling concept based on a 
session storage and session item. The session storage is responsible for 
get and set the session data and the session itself is implemented as a
mongo storage item. See m01.mongo for more information about storage/item
pattern.

Note: This concept requires a session adapter registration which is able to
setup the correct storage and session item. See the sample below for more
information e.g.:

  zope.component.provideAdapter(getSampleSession, (IRequest,), ISampleSession)

Note: one of the most important part in any session implementation is that
a session implementation doesn't write to the database if nothing changed.
Otherwise you will get quickly into trouble. We prevent this by ensure that
we never write similar values back to the mongo item and force them to get
marked as changed (_m_changed). See m01.mongo for more information about
the built in transaction handling.


Session
-------

Let's define a sample session:

  >>> import zope.schema
  >>> import zope.interface
  >>> import m01.session.client
  >>> import m01.session.session
  >>> import m01.session.interfaces

  >>> from zope.publisher.interfaces import IRequest
  >>> from zope.session.interfaces import IClientId
  >>> from m01.mongo.fieldproperty import MongoFieldProperty

  >>> class ISampleSession(m01.session.interfaces.ISession):
  ...     """Sample session interface"""
  ... 
  ...     boolean = zope.schema.Bool(
  ...         title=u'boolean',
  ...         description=u'boolean',
  ...         default=False,
  ...         required=False)
  ... 
  ...     integer = zope.schema.Int(
  ...         title=u'integer',
  ...         description=u'integer',
  ...         default=None,
  ...         required=False)
  ... 
  ...     text = zope.schema.TextLine(
  ...         title=u'text',
  ...         description=u'text',
  ...         default=None,
  ...         required=False)

  >>> class SampleSession(m01.session.session.Session):
  ...     """Sample session"""
  ... 
  ...     zope.interface.implements(ISampleSession)
  ... 
  ...     boolean = MongoFieldProperty(ISampleSession['boolean'])
  ...     integer = MongoFieldProperty(ISampleSession['integer'])
  ...     text = MongoFieldProperty(ISampleSession['text'])
  ... 
  ...     dumpNames = ['boolean', 'integer', 'text']

Let's define a session storage:

  >>> import m01.mongo.testing
  >>> class SampleSessionStorage(m01.session.session.SessionStorage):
  ...     """Sample session storage"""
  ...
  ...     @property
  ...     def collection(self):
  ...         db = m01.mongo.testing.getTestDatabase()
  ...         return db['test_session_storage']
  ...
  ...     def load(self, data):
  ...         """Create a session based on the given key"""
  ...         _type = data['_type']
  ...         if _type == 'SampleSession':
  ...             return SampleSession(data)
  ...         else:
  ...             raise TypeError("No class found for _type %s" % _type)
  ...
  ...     def createSession(self, key, md5Key):
  ...         data = {'__name__': md5Key}
  ...         """Create a session based on the given key"""
  ...         if key == 'ISampleSession':
  ...             return SampleSession(data)
  ...         else:
  ...             raise TypeError("No class found for session key %s" % key)

Now register a session adapter using our session storage and session

  >>> def getSampleSession(request):
  ...     storage = SampleSessionStorage(request)
  ...     return storage.get('ISampleSession')

  >>> zope.component.provideAdapter(getSampleSession, (IRequest,),
  ...     ISampleSession)

Now we need to setup a participation (request):

  >>> from cStringIO import StringIO
  >>> from zope.publisher.http import HTTPRequest
  >>> request = HTTPRequest(StringIO(''), {})

And we need a IClientId Adapter:

  >>> namespace = 'zope3_cs_123'
  >>> secret = 'very secure'
  >>> mcim = m01.session.client.ClientIdFactory(namespace, secret)
  >>> zope.component.provideAdapter(mcim, (IRequest,), provides=IClientId)

The simplest way to use a session is to call the session adapter with a
request. As you can see we will get the same session with the same session id:

  >>> session = ISampleSession(request)
  >>> session
  <SampleSession u'...'>

We can now access the data from the session.

  >>> session.boolean
  False

  >>> session.boolean = True

  >>> session.integer
  >>> session.integer = 42

  >>> session.text
  >>> session.text = u'foobar'

Since the session storage is transaction aware we need to commit the
transaction to store the session data in our mongodb.

  >>> import transaction
  >>> transaction.commit()

Let's get the session again and check our previous added values:

  >>> session = ISampleSession(request)

  >>> session.boolean
  True

  >>> session.integer
  42

  >>> session.text
  u'foobar'


Now we can read the session data again from mongodb. Normaly you can't do this
because we don't know the real key for the stored session data. But we can
simply check our fake mongodb:

  >>> db = m01.mongo.testing.getTestDatabase()
  >>> collection = db['test_session_storage']
  >>> collection.count()
  1

  >>> res = collection.find_one({'text': 'foobar'})
  >>> m01.mongo.testing.reNormalizer.pprint(res)
  {u'__name__': u'...',
   u'_id': ObjectId('...'),
   u'_type': u'SampleSession',
   u'_version': 1,
   u'boolean': True,
   u'created': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'integer': 42,
   u'modified': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'text': u'foobar'}


tear down
---------

Now tear down our MongoDB database with our current test connection:

  >>> conn = m01.mongo.testing.getTestConnection()
  >>> conn.drop_database('test_session_storage')
