###############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: interfaces.py 3513 2012-12-09 05:01:26Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.i18nmessageid
import zope.schema
from zope.schema import vocabulary

import m01.mongo.interfaces
import p01.session.interfaces

_ = zope.i18nmessageid.MessageFactory('p01')


SEARCH_SESSION = u'm01.search.interfaces.ISearchSession'

AND = 'AND'
NOT = 'NOT'
OR = 'OR'

NOVALUE = object()


connectorVocabulary = vocabulary.SimpleVocabulary([
    vocabulary.SimpleTerm(OR, title=_('or')),
    vocabulary.SimpleTerm(AND, title=_('and')),
    vocabulary.SimpleTerm(NOT, title=_('not')),
    ])

class ISearchCriterion(m01.mongo.interfaces.IMongoSubItem):
    """Search criteria base class

    Search criterion are implemented as filter sub items stored as criterias

    Note: you have to define your own query and search concept. The 
    SearchFilter and SearchCriterion classes do not know anything about how
    to search. The m01.searcher only offers a search filter management.

    """

    __name__ = zope.schema.TextLine(
        title=u'Name',
        description=u'Locatable criterion name.',
        required=True)

    title = zope.schema.TextLine(
        title=_(u'Title'),
        description=_(u'Title'),
        required=True)

    label = zope.schema.TextLine(
        title=u'Operator label',
        description=u'Operator label',
        required=True)

    weight = zope.schema.Int(
        title=u'Order marker',
        description=u'Order marker',
        default=0,
        required=True)

    single = zope.schema.Bool(
        title=u'Single criterion',
        description=u'Single criterion',
        default=False,
        required=True)

    # we can't use a TextLine field or we can't use schema validation in
    # criteria
    value = zope.schema.Field(
        title=_(u'Search value'),
        description=_(u'Search value'),
        required=False)

    # non persistent (volatile) property for store the current result
    total = zope.schema.Int(
        title=u'Total',
        description=u'Total',
        default=0,
        required=False)

    def search():
        """Returns the search result as python set or None

        The default value None get ignored from connector chaining. But that's
        probably up to your own implementation. At least you should expect None
        as a possible value if you chain the different result sets.

        Each criterion could do an own search or enhance a given search query
        within the query method.

        """

    def query(query):
        """Enhance the given query or return the query unchanged"""


class ISearchCriterionWithConnector(ISearchCriterion):
    """Search criteria with connector

    This search criterion offers an AND/NOT/OR connector

    """

    connector = zope.schema.Choice(
        title=u'Connector',
        description=u'Connector',
        vocabulary=connectorVocabulary,
        default=OR,
        required=True)


class ITextSearchCriterion(ISearchCriterion):
    """TextLine value criterion"""

    value = zope.schema.TextLine(
        title=_(u'Search value'),
        description=_(u'Search value'),
        required=False)


class ISearchFilterStorage(m01.mongo.interfaces.IMongoStorage):
    """Search filter storage"""

    def copySearchFilter(obj):
        """Copy given search filter and return a new instance of them."""

    def add(obj):
        """Add a given SearchFilter

        The given SearchFilter object could be an already existing item. The
        current implementation will call the copySearchFilter method an prevent
        to add bad items.

        """


class ISearchFilter(m01.mongo.interfaces.IMongoStorageItem):
    """Search filter base class

    Note: this search filter can get stored in memcached or mongodb.
    If we setup a new filter and configure them, we store them in
    memcached. Later we can optional store the filter in mongodb within our
    SearchFilterStorage. Our SearchSession knows how to store and load such
    SearchFilter. The SearchSession also keeps loaded filters persistent
    along a search session for it's relevant search form.

    Note: you have to define your own query and search concept. The 
    SearchFilter and SearchCriterion classes do not know anything about how
    to search. The m01.searcher only offers a search filter management.

    """

    # filter name used if added to SearchFilterStorage
    name = zope.schema.TextLine(
        title=_(u'Filter Name'),
        description=_(u'Filter Name'),
        required=False)

    criterionFactories = zope.schema.Dict(
        title=u'Name/criterion factory dictionary',
        description=u'Name/criterion factory dictionary',
        required=True,
        default={})

    availableCriterionFactories = zope.schema.Dict(
        title=u'Available name/criterion factory dictionary',
        description=u'Available name/criterion factory dictionary',
        required=True,
        default={})

    # criteria (list of criterion)
    criteria = m01.mongo.schema.MongoList(
        title=_(u'Criteria'),
        description=_(u'Criteria'),
        value_type=zope.schema.Object(
            schema=ISearchCriterion,
        ),
        default=[],
        required=False)

    def clear():
        """Remove all filter criteria."""

    def createCriterion(name, value=NOVALUE):
        """Create a criterion by factory name."""

    def addCriterion(criterion):
        """Add a criterion by name at the end of the list."""

    def createAndAddCriterion(name, value=NOVALUE):
        """Create and add a criterion by name at the end of the list."""

    def removeCriterion(criterion):
        """Add a criterion by name at the end of the list."""


class ISearchSession(p01.session.interfaces.ISession):
    """Search session supporting API for filter management.

    Filters contain the criterion rows and are stored persistent

    The methods support a key argument. This could be a context reference key
    give from the IntId utility or some other discriminator.  If we do not 
    support a key, the string ``default`` is used.
    """

    filters = zope.schema.Dict(
        title=u'Dict of search filter',
        description=u'Dict of search filter data',
        key_type=zope.schema.Field(),
        value_type=zope.schema.Dict(),
        default={},
        required=False)

    def load(data):
        """Load data into a ISearchFilter"""

    def saveFilterData(self, name, data):
        """Save new or existing filter data"""

    def getFilter(name):
        """Return search filter by name."""

    def getFilters(name):
        """Return a list of search filters."""

    def addFilter(name, searchFilter):
        """Add search filter."""

    def removeFilter(name):
        """Remove search filter."""
