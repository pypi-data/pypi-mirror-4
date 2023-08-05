======
README
======

This package provides an advanced search filter management framework based on
on our mongodb library called m01.mongo. The different components can be used
to build search filter with different criterion.

NOTE: this framework does NOT define a search concept and does not know
anything about how to search. This package only offers a filter and criteria
management. You have to enhance the criterion or filter or both for implement
and optimize your own advanced search concept.

A search filter contains one or more search filter criteria. Each criteria
defines an operation e.g. and/or. The search filter and search criteria can
get cached in memcache or stored in mongodb.



Condition
---------

Befor we start testing, check if our thread local cache is empty or if we have
left over some junk from previous tests:

  >>> from pprint import pprint
  >>> from m01.mongo import LOCAL
  >>> pprint(LOCAL.__dict__)
  {}


Setup
-----

First import some components:

  >>> import datetime
  >>> import transaction
  >>> import zope.component

  >>> import m01.mongo
  >>> import m01.mongo.base
  >>> import m01.mongo.container
  >>> import m01.mongo.testing
  >>> import m01.searcher.testing

We also need a application root object. Let's define a static MongoContainer
as our application database root item.

  >>> class MongoRoot(m01.mongo.container.MongoContainer):
  ...     """Mongo application root"""
  ... 
  ...     _id = m01.mongo.getObjectId(0)
  ... 
  ...     def __init__(self):
  ...         pass
  ... 
  ...     @property
  ...     def collection(self):
  ...         return m01.mongo.testing.getRootItems()
  ...
  ...     @property
  ...     def cacheKey(self):
  ...         return 'root'
  ... 
  ...     def load(self, data):
  ...         """Load data into the right mongo item."""
  ...         return m01.searcher.testing.SampleStorage(data)
  ... 
  ...     def __repr__(self):
  ...         return '<%s %s>' % (self.__class__.__name__, self._id)


As you can see our MongoRoot class defines a static mongo ObjectID as _id. This
means the same _id get use every time. This _id acts as our __parent__
reference.

The following method allows us to generate new MongoRoot item instances. This
allows us to show that we generate different root items like we whould do on a
server restart.

  >>> def getRoot():
  ...     return MongoRoot()

Here is our database root item:

  >>> root = getRoot()
  >>> root
  <MongoRoot 000000000000000000000000>

  >>> root._id
  ObjectId('000000000000000000000000')


Search Criterion
----------------

See testing for more info:

  >>> from m01.searcher.testing import ValueCriterion
  >>> ValueCriterion
  <class 'm01.searcher.testing.ValueCriterion'>


Search Filter
-------------

Now we are ready and can start with our search filter implementation.
As you know each filter must define ist own query concept. This sample uses
a simple query plan where each criterion returns a mongo query where we can 
use for build a complex query.

  >>> from m01.searcher import interfaces
  >>> from m01.searcher.testing import SampleSearchFilter

Now let's setup the filter:

  >>> mySearchFilter = SampleSearchFilter({})

and add a criterion:

  >>> valueCriterion = mySearchFilter.createAndAddCriterion('values')
  >>> valueCriterion

as you can see, we have a filter with one criterion:

  >>> m01.mongo.testing.reNormalizer.pprint(mySearchFilter.dump())
  {'__name__': u'...',
   '_id': ObjectId('...'),
   '_type': u'SampleSearchFilter',
   '_version': 0,
   'created': datetime(..., tzinfo= ...),
   'criteria': [{'_id': ObjectId('...'),
                 '_type': u'ValueCriterion',
                 'created': datetime(..., tzinfo= ...),
                 'weight': 0}]}

Let's add another criterion:

and add a criterion with a search value:

  >>> valueCriterion2 = mySearchFilter.createAndAddCriterion('values', u'foo')
  >>> valueCriterion2

  >>> m01.mongo.testing.reNormalizer.pprint(mySearchFilter.dump())
  {'__name__': u'...',
   '_id': ObjectId('...'),
   '_type': u'SampleSearchFilter',
   '_version': 0,
   'created': datetime(..., tzinfo= ...),
   'criteria': [{'_id': ObjectId('...'),
                 '_type': u'ValueCriterion',
                 'created': datetime(..., tzinfo= ...),
                 'modified': datetime(..., tzinfo= ...),
                 'value': u'foo',
                 'weight': 0},
                {'_id': ObjectId('...'),
                 '_type': u'ValueCriterion',
                 'created': datetime(..., tzinfo= ...),
                 'weight': 0}]}


Search Session
--------------

Let's register and create a search session. Such a search session implicit
stores the search filter in memcache. Since only store the raw mongo item
data in our session, the SearchSession knows how to load dumped SearchFilter
data. Let's implement a custom search session:

  >>> from m01.searcher.testing import ISampleSearchSession
  >>> from m01.searcher.testing import SampleSearchSession

and register the session:

  >>> zope.component.provideAdapter(SampleSearchSession)

Now we can create a test request and get the session adapter:

  >>> from cStringIO import StringIO
  >>> from zope.publisher.http import HTTPRequest
  >>> request = HTTPRequest(StringIO(''), {})

  >>> searchSession = ISampleSearchSession(request)
  >>> searchSession
  <SampleSearchSession '...'>

The search session offers an API for store and manage filters: 

  >>> searchSession.addFilter('myFilter', mySearchFilter)

And we can get such filters from the search session by name.

  >>> sf = searchSession.getFilter('myFilter')
  >>> sf
  <SampleSearchFilter u'...'>

  >>> sfDump = sf.dump()
  >>> m01.mongo.testing.reNormalizer.pprint(sfDump)
  {'__name__': u'...',
   '_id': ObjectId('...'),
   '_type': u'SampleSearchFilter',
   '_version': 0,
   'created': datetime(..., tzinfo= ...),
   'criteria': [{'_id': ObjectId('...'),
                 '_type': u'ValueCriterion',
                 'created': datetime(..., tzinfo= ...),
                 'modified': datetime(..., tzinfo= ...),
                 'value': u'foo',
                 'weight': 0},
                {'_id': ObjectId('...'),
                 '_type': u'ValueCriterion',
                 'created': datetime(..., tzinfo= ...),
                 'weight': 0}]}

An important part is that our load method does not pop values from the
SessionData dict. Let's ensure that we can get the same data again:

  >>> sf2 = searchSession.getFilter('myFilter')
  >>> sf2
  <SampleSearchFilter u'...'>

  >>> sf2Dump = sf2.dump()
  >>> sfDump == sf2Dump
  True

  >>> m01.mongo.testing.reNormalizer.pprint(sf2.dump())
  {'__name__': u'...',
   '_id': ObjectId('...'),
   '_type': u'SampleSearchFilter',
   '_version': 0,
   'created': datetime(..., tzinfo= ...),
   'criteria': [{'_id': ObjectId('...'),
                 '_type': u'ValueCriterion',
                 'created': datetime(..., tzinfo= ...),
                 'modified': datetime(..., tzinfo= ...),
                 'value': u'foo',
                 'weight': 0},
                {'_id': ObjectId('...'),
                 '_type': u'ValueCriterion',
                 'created': datetime(..., tzinfo= ...),
                 'weight': 0}]}

Or we can get all search filters stored in this session:

  >>> searchSession.getFilters()
  [<SampleSearchFilter u'...'>]

And we can remove a filter by it's name:

  >>> searchSession.removeFilter('myFilter')
  >>> searchSession.getFilters()
  []

Now let's add another filter:

  >>> myOtherFilter = SampleSearchFilter({})
  >>> searchSession.addFilter('other', myOtherFilter)
  >>> searchSession.getFilter('other')
  <SampleSearchFilter u'...'>

  >>> searchSession.getFilters()
  [<SampleSearchFilter u'...'>]

Now let's remove the filter and cleanup our search session:

  >>> searchSession.removeFilter('other')
  >>> searchSession.getFilters()
  []
