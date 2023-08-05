###############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: filter.py 3072 2012-09-06 03:43:55Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface

import m01.mongo.base
import m01.mongo.item
import m01.mongo.util
from m01.mongo.fieldproperty import MongoFieldProperty

from m01.searcher import interfaces


class SearchFilterStorageMixin(object):
    """SearchFilterStorage mixin class providing filter cleanup before add"""

    def copySearchFilter(self, obj):
        """Copy given search filter and return a new instance of them."""
        data = obj.dump()
        data.pop('_id', None)
        data.pop('_pid', None)
        data.pop('_version', None)
        data.pop('__name__', None)
        data.pop('created', None)
        data.pop('modified', None)
        criteria = []
        for d in data.pop('criteria', []):
            d.pop('_id', None)
            d.pop('created', None)
            d.pop('modified', None)
            criteria.append(d)
        data['criteria'] = criteria
        return obj.__class__(data)

    def add(self, obj):
        """Add a (copy of a) given SearchFilter

        The given SearchFilter object could be an already existing item. Let's
        just replace all the mongo _id and core attributes found in the given
        filter and criterions.
        
        """
        cleanFilter = self.copySearchFilter(obj)
        return super(SearchFilterStorageMixin, self).add(cleanFilter)


class SearchFilterStorage(SearchFilterStorageMixin,
    m01.mongo.base.MongoStorageBase):
    """Search filter storage (optional)"""

    zope.interface.implements(interfaces.ISearchFilterStorage)


class SearchFilter(m01.mongo.item.MongoStorageItem):
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
    zope.interface.implements(interfaces.ISearchFilter)

    # define your own criterion factories,
    # criterionFactories = {'key': MyCriterionClass}
    criterionFactories = {}

    name = MongoFieldProperty(interfaces.ISearchFilter['name'])
    criteria = MongoFieldProperty(interfaces.ISearchFilter['criteria'])

    # ignore parent _pid reference
    _skipNames = ['__name__']
    _dumpNames = ['_id', '_type', '_version', '__name__',
                  'created', 'modified',
                  'name', 'criteria']

    # generic converter which knows how to load the correct criterion based on
    # criterionFactories. See m01.mongo for more information about converters
    @property
    def converters(self):
        criterionFactories = self.criterionFactories.values()
        def convertCriterion(d):
            _type = d.get('_type')
            for cls in criterionFactories:
                if _type == cls.__name__:
                    # clone data dict or we will pop values from our original
                    # data
                    return cls(dict(d))
        return {'criteria': convertCriterion}

    @property
    def availableCriterionFactories(self):
        """Returns only available not duplicated (single) criterion factories"""
        # we compare criterion factory class names for find duplicated
        #  factories with existing criteria instance class names. Use another
        # concept if this doesn't fit for your implementation
        existing = [c.__class__.__name__ for c in self.criteria]
        for key, cr in self.criterionFactories.items():
            if (not cr.single) or (cr.single and cr.__name__ not in existing):
                yield key, cr

    @property
    def __name__(self):
        return unicode(self._id)

    # criteria management api
    def clear(self):
        """See interfaces.ISearchFilter"""
        self.criteria = m01.mongo.util.MongoItemsData()

    def createCriterion(self, key, value=interfaces.NOVALUE):
        """Create a criterion."""
        factory = self.criterionFactories[key]
        criterion = factory({'__parent__': self})
        if value is not interfaces.NOVALUE:
            criterion.value = value
        return criterion

    def addCriterion(self, criterion):
        """See interfaces.ISearchFilter"""
        self.criteria.insert(0, criterion)

    def createAndAddCriterion(self, key, value=interfaces.NOVALUE):
        criterion = self.createCriterion(key, value)
        return self.addCriterion(criterion)

    def removeCriterion(self, criterion):
        """See interfaces.ISearchFilter"""
        self.criteria.remove(criterion)
