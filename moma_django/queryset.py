#==========================================================================
# Copyright 2012 Lucidel, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this work except in compliance with the License.
# You may obtain a copy of the License in the LICENSE file, or at:
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#==========================================================================

from django.db.models.query_utils import Q
from .query import MongoQuery

class MongoQuerySet(object):
    
    def __init__(self, model=None, query=None):
        self.model = model
        self.query = query or MongoQuery(self.model)
        self.flat = False
        
    def __len__(self):
        return self.count()
    
    def __iter__(self):
        #result cache should be used
        return self.iterator()

    def __getitem__(self, k):
        """
        Retrieves an item or slice from the set of results.
        """
        if not isinstance(k, (slice, int, long)):
            raise TypeError
        
        cursor = self.cursor()
        
        if isinstance(k, (int, long)):
            return self._handle_result_item(cursor.__getitem__(k))
        else:
            return map(self._handle_result_item, cursor.__getitem__(k))
        
    def _clone(self):
        query = self.query.clone()
        c = self.__class__(self.model, query)
        c.flat = self.flat
        return c
    
    def _model_attributes(self):
        if not hasattr(self, '_model_attributes_cache'):
            attributes = {}
            
            for f in self.model._meta.fields:
                attr, column = f.get_attname_column()
                attributes[column] = (attr, f)
                
            self._model_attributes_cache = attributes
        
        return self._model_attributes_cache
    
    def _create_object_from_response(self, item):
        obj = self.model()
        #{db_column: [model_attribute, field],...}
        attributes = self._model_attributes()
        
        for column_name, value in item.items():
            #FIXME: datetime should be converted to date for datetime field
            try:
                attr, field = attributes[column_name]
                setattr(obj, attr, field.to_python(value))
            except KeyError:
                pass
        obj._state.adding = False
        return obj
    
    def _create_values_from_response(self, item):
        meta = self.model._meta
        fields = self.query.get_fields()
        
        if self.flat:
            f = meta.get_field(fields[0])
            return f.to_python(item[f.get_attname_column()[1]])
        else:
            output = {}
            for field_name in fields:
                f = meta.get_field(field_name)
                output[field_name] = f.to_python(item[f.get_attname_column()[1]])
            return output   
         
    def _handle_result_item(self, item):
        if self.query.fields:
            return self._create_values_from_response(item)
        else:
            return self._create_object_from_response(item)
    
    def cursor(self):
        return self.query.get_result()
    
    def iterator(self):
        #result cache should be used
        cursor = self.cursor()
        if cursor:
            for item in cursor:
                yield self._handle_result_item(item)
    
    def select_related(self, *fields, **kwargs):
        #FIXME: Does not work for now
        return self._clone()
    
    def get(self, *args, **kwargs):
        clone = self.filter(*args, **kwargs)
        if self.query.can_filter():
            clone = clone.order_by()

        num = len(clone)
        if num == 1:
            return clone[0]
        if not num:
            raise self.model.DoesNotExist("%s matching query does not exist."
                    % self.model._meta.object_name)
        raise self.model.MultipleObjectsReturned("get() returned more than one %s -- it returned %s! Lookup parameters were %s"
                % (self.model._meta.object_name, num, kwargs))

    def values_list(self, *args, **kwargs):
        qs = self._clone()
        qs.flat = bool(kwargs.get('flat', False))
        qs.query.set_fields(args)
        return qs
    
    def order_by(self, *args):
        qs = self._clone()
        qs.query.clear_ordering()        
        qs.query.add_ordering(args)
        return qs
    
    def count(self):
        return self.query.get_count()
    
    def using(self, using):
        return self._clone()

    def _using_collection_prefix(self, using_prefix=None):
        """
        This method enables redirecting the entire model onto another collection.
        Note: this should be used VERY carefully as it will redirect all reading and writing.
        Use using_prefix=None to cancel the redirection.
        E.g. if using_prefix='acme_' and the db name is 'customers', a new db will be used, called 'acme_customers'.
        """
        self.query._setTargetCollectionPrefix(using_prefix)

    def exists(self):
        return self.query.has_results()
    
    def exclude(self, *args, **kwargs):
        return self._filter_or_exclude(True, *args, **kwargs)
    
    def filter(self, *args, **kwargs):
        return self._filter_or_exclude(False, *args, **kwargs)
    
    def all(self, **kwargs):
        return self._clone()

    def delete(self):
        assert self.query.can_filter(), \
                "Cannot use 'limit' or 'offset' with delete."
                
        del_query = self._clone()
        del_query.query.delete()

    delete.alters_data = True
    
    def _filter_or_exclude(self, negate, *args, **kwargs):
        if args or kwargs:
            assert self.query.can_filter(), \
                    "Cannot filter a query once a slice has been taken."

        clone = self._clone()
        if negate:
            clone.query.add_q(~Q(*args, **kwargs))
        else:
            clone.query.add_q(Q(*args, **kwargs))
        return clone
#        for filter, value in kwargs.items():
#            clone.query.add_q(MongoQ(negate, filter, value))
#        return clone
    
    def insert(self, items):
        if items:
            return self.query.insert(items)
        
    #These maybe should be delivered directly to query from __getattr__
    def ensure_index(self, *args, **kwargs):
        return self.query.collection.ensure_index(*args, **kwargs)
    
    def drop_indexes(self):
        return self.query.collection.drop_indexes()
    
    def index_information(self):
        return self.query.collection.index_information()
    
    def reindex(self):
        return self.query.collection.reindex()

    def complex_filter(self, filter_obj):
        """
        Returns a new QuerySet instance with filter_obj added to the filters.

        filter_obj can be a Q object (or anything with an add_to_query()
        method) or a dictionary of keyword lookup arguments.

        This exists to support framework features such as 'limit_choices_to',
        and usually it will be more natural to use other methods.
        """
        if isinstance(filter_obj, Q) or hasattr(filter_obj, 'add_to_query'):
            clone = self._clone()
            clone.query.add_q(filter_obj)
            return clone
        else:
            return self._filter_or_exclude(None, **filter_obj)

    def _update(self, values):
        assert self.query.can_filter(), \
                "Cannot update a query once a slice has been taken."        
        
        data = {}
        
        for field, model, value in values:
            data[field.name] = value

        self.query.update(data)