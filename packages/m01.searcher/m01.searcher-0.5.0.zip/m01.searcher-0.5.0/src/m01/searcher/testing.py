###############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: testing.py 3072 2012-09-06 03:43:55Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema
from zope.publisher.interfaces import IRequest

import m01.mongo.interfaces
import m01.mongo.item
import m01.mongo.schema
import m01.mongo.storage
import m01.mongo.testing
from m01.mongo.fieldproperty import MongoFieldProperty

import  m01.session.testing

import m01.searcher.criterion
import m01.searcher.filter
import m01.searcher.session
from m01.searcher import interfaces


class ISampleStorage(m01.mongo.interfaces.IMongoStorage):
    """Sample storage interface."""


class SampleStorage(m01.mongo.testing.TestCollectionMixin,
    m01.mongo.storage.MongoStorage):
    """Sample storage."""

    zope.interface.implements(ISampleStorage)

    def __init__(self):
        pass

    def load(self, data):
        """Load data into the right mongo item."""
        return SampleContent(data)


class ValueCriterion(m01.searcher.criterion.SearchCriterion):
    """Value search criterion"""

    title = u'My Value Search'

    @property
    def updateQuery(self, query):
        if self.connector == interfaces.OR:
            query = {'$and': [query, {'value': self.value}]}
        elif self.connector == interfaces.AND:
            query['value'] = self.value
        elif self.connector == interfaces.NOT:
            query['value'] = {'$ne': self.value}


class SampleSearchFilter(m01.searcher.filter.SearchFilter):
    """Sample search filter"""

    criterionFactories = {'values': ValueCriterion}


class SampleSessionStorage(m01.session.session.SessionStorage):
    """Sample session storage"""

    @property
    def collection(self):
        db = m01.mongo.testing.getTestDatabase()
        return db['test_session_storage']

    def load(self, data):
        """Create a session based on the given key"""
        _type = data['_type']
        if _type == 'SampleSession':
            return SampleSearchSession(data)
        else:
            raise TypeError("No class found for _type %s" % _type)

    def createSession(self, key, md5Key):
        data = {'__name__': md5Key}
        """Create a session based on the given key"""
        if key == 'ISampleSearchSession':
            return SampleSearchSession(data)
        else:
            raise TypeError("No class found for session key %s" % key)


class ISampleSearchSession(interfaces.ISearchSession):
    """SampleSearchSession"""


def getSearchFilter(data):
    """Search filter creator"""
    _type = data['_type']
    if _type == 'SampleSearchFilter':
        return SampleSearchFilter(data)
    else:
        raise TypeError("No class found for _type %s" % _type)
        

class SampleSearchSession(m01.searcher.session.SearchSession):

    zope.interface.implementsOnly(ISampleSearchSession)

    def load(self, data):
        return SampleSearchFilter(data)


@zope.component.adapter(IRequest)
@zope.interface.implementer(ISampleSearchSession)
def getSampleSearchSession(request):
    sampleSessionStorage = SampleSessionStorage(request)
    return sampleSessionStorage.get('ISampleSearchSession')


def setUp(test):
    m01.mongo.testing.setUpStubMongoDB(test)
    m01.session.testing.setUpSessionClientId()


def tearDown(test):
    m01.mongo.testing.tearDownStubMongoDB(test)
