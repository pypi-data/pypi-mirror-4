###############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: criterion.py 3072 2012-09-06 03:43:55Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.location.location

import m01.mongo.item
from m01.mongo.fieldproperty import MongoFieldProperty

from m01.searcher import interfaces
from m01.searcher.interfaces import _


class SearchCriterion(m01.mongo.item.MongoSubItem,
    zope.location.location.Location):
    """Search criteria base class

    Search criterion are implemented as filter sub items stored in a list of
    criterias.

    REmember: you have to define your own query setup and search concept. The 
    SearchFilter and SearchCriterion classes do not know anything about how
    to search. The m01.searcher only offers a search filter management.

    """
    zope.interface.implements(interfaces.ISearchCriterion)

    _total = None # by default None

    # customize this in your own criterion
    title = None
    label = _('equals')
    single = False

    weight = MongoFieldProperty(interfaces.ISearchCriterion['weight'])
    value = MongoFieldProperty(interfaces.ISearchCriterion['value'])

    _skipNames = ['__name__', 'single', 'total']
    _dumpNames = ['_id', '_type', 'created', 'modified',
                  'weight', 'value']

    # the total is a non persistent (volatile) property (not stored in mongodb)
    @apply
    def total():
        def fget(self):
            return self._total
        def fset(self, value):
            self._total = value
        return property(fget, fset)

    def search(self):
        """Returns the search result as python set or None

        The default value None get ignored from connector chaining. But that's
        probably up to your own implementation. At least you should expect None
        as a possible value if you chain the different result sets.

        Each criterion could do an own search or enhance a given search query
        within the query method.

        """
        return None

    def query(self, query):
        """Enhance the given query or return the query unchanged"""
        return query


class SearchCriterionWithConnector(SearchCriterion):
    """Search criteria base class

    This enhanced search criterion offers an AND/NOT/OR connector

    """
    zope.interface.implements(interfaces.ISearchCriterionWithConnector)

    _dumpNames = ['_id', '_type', 'created', 'modified',
                  'weight', 'value', 'connector']

    connector = MongoFieldProperty(
        interfaces.ISearchCriterionWithConnector['connector'])