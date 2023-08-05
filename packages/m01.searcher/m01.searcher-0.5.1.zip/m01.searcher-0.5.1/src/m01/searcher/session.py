###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: session.py 3513 2012-12-09 05:01:26Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface

from zope.security.proxy import removeSecurityProxy

import m01.mongo
from m01.mongo import UTC
from m01.mongo.fieldproperty import MongoFieldProperty

import p01.session.session
from m01.searcher import interfaces
from m01.searcher.interfaces import SEARCH_SESSION


def toPickableDatetime(dt=None):
    """Replace bson.tz_util.FixOffset with pickable UTC"""
    if dt:
        dt = dt.replace(tzinfo=UTC)
    return dt


class SearchSession(p01.session.session.Session):
    """Search session base class
    
    NOTE: only one filter within the same filterName ist stored in this session

    This means we will add new search filter to our filters item list or
    replace an existing filter. Note, that our fiter get added by it's
    filterName which is NOT the mongo storage item __name__. This means
    we have to iterate our filter list for find the right filter.

    """

    zope.interface.implementsOnly(interfaces.ISearchSession)

    @property
    def filters(self):
        return self.__getitem__(SEARCH_SESSION)

    def load(self, data):
        """Load data into a ISearchFilter"""
        raise NotImplementedMethod("Subclass must implement the load method")

    def saveFilterData(self, filterName, data):
        """Save new or update existing filter data

        Note: we will remove the __parent__ reference which prevents that we
        assign a reference to a not loaded object if we load the SearchFilter.

        """
        # data could be a SessionData instance, create new dict and prevent
        # that we never store a SessionData instance in memcached
        data = m01.mongo.dictify(data)
        # remove __parent__ reference
        data.pop('_pid', None)
        # replace with pickable datetime
        data['created'] = toPickableDatetime(data.pop('created', None))
        data['modified'] = toPickableDatetime(data.pop('modified', None))
        criteria = []
        for d in data.pop('criteria', []):
            # replace with pickable datetime
            d['created'] = toPickableDatetime(d.pop('created', None))
            d['modified'] = toPickableDatetime(d.pop('modified', None))
            criteria.append(d)
        data['criteria'] = criteria
        self.filters[filterName] = dict(data)

    def addFilter(self, filterName, searchFilter):
        """Add search filter
        
        This method dumps the SearchFilter data and stores them in a session.
        The load method must be able to load the dumped data back into a
        SearchFilter. See dump method for more info. 
        
        """
        data = removeSecurityProxy(searchFilter).dump(dictify=True)
        self.saveFilterData(filterName, data)

    def getFilter(self, filterName):
        """Return search filter by name."""
#        data = self.filters.get(filterName, None)
        data = self.filters.get(filterName, None)
        if data is not None:
            # clone data dict or we will pop values from our original data
            return self.load(dict(data))

    def getFilters(self):
        """Return a list of search filters."""
        res = []
        append = res.append
        for data in self.filters.values():
            # clone data dict or we will pop values from our original data
            append(self.load(dict(data)))
        return res

    def removeFilter(self, filterName):
        """Remove search filter."""
        if filterName in self.filters:
            del self.filters[filterName]
