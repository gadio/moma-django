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

from copy import deepcopy
from django.utils.tree import Node
from .query_utils import fix_value
import pymongo
from pymongo.errors import AutoReconnect
from .exceptions import MongoQuerySetExeption
from django.conf import settings
from .query_utils import MongoQ, negate_where_clause

HOST = getattr(settings, 'MONGO_HOST', 'localhost')
PORT = getattr(settings, 'MONGO_PORT', 27017)
COLLECTION = getattr(settings, 'MONGO_COLLECTION')

try:
    connection = pymongo.Connection(HOST, PORT)
except (pymongo.errors.AutoReconnect, pymongo.errors.ConfigurationError):
    connection = None

class FakeCollection(object):

    def find(self, *args, **kwargs):
        return []
    
    def __getattr__(self, name):
        def fake_method(*args, **kwargs):
            return
        return fake_method

def get_collection(model, use_collection_name_prefix=None, override_default_db_name=False):
    collection_name = COLLECTION
    try:
        from django.db import connections
        default_connection = connections['default']
        default_db_name = default_connection.settings_dict['NAME']
        # the 'test_' is for a full sql db (e.g. mysql). The ':memory:' is for testing situation with sqlite as the main db
        if (not override_default_db_name) and default_db_name == ':memory:':
            collection_name = 'test_'+collection_name
        elif (not override_default_db_name) and default_db_name.startswith('test_'):
            collection_name = default_db_name
        if use_collection_name_prefix is not None:
            collection_name = use_collection_name_prefix + collection_name
    except Exception:
        pass

    if not connection:
        return FakeCollection()
    
    # NOTE - the following command ensures that the mongo will use a different database name once running in a unit test mode
    # usually, the default DB name is prepended with "test_" for the default SQL db. The MongoDB will follow. This ensures
    # that in unit-test situation, the database will change without affecting the original database
    db = connection[collection_name]

    opt = model._meta
    name = '%s_%s' % (opt.app_label, opt.object_name.lower())
    return db[name]

class MongoQuery(object):
    AND = 'AND'
    OR = 'OR'
    COLON = ':'
    DEFAULT = 'DEFAULT'

    def __init__(self, model):
        self.model = model
        self.where = Node()
        self.order_by = []
        self.fields = set()
        self.default_ordering = True
        self.select_related = True #Hack for admin-interface: django/contrib/admin/views/main.py line 210
        self._field_names = {}
        self.target_collection_prefix=None

    def _setTargetCollectionPrefix(self, prefix_str=None):
        """
        This method enables redirecting the entire model onto another collection.
        Note: this should be used VERY carefully as it will redirect all reading and writing.
        Use prefix_str=None to cancel the redirection.
        E.g. if prefix_str='acme_' and the db name is 'customers', a new db will be used, called 'acme_customers'.
        """
        self.target_collection_prefix=prefix_str

    def _column_name(self, field_name):
        if isinstance(field_name, (list, tuple)):
            return [self._column_name(f) for f in field_name]
        
        if not field_name in self._field_names:
            opt = self.model._meta

            if field_name == 'pk':
                field = opt.pk
            else:
                field = opt.get_field(field_name)
            
            self._field_names[field_name] = field.get_attname_column()[1]
        
        return self._field_names[field_name]

    def clear_ordering(self, force_empty=False):
        self.order_by = []
        if force_empty:
            self.default_ordering = False
        
    def add_ordering(self, ordering):
        if ordering:
            self.order_by.extend(ordering)
        else:
            self.default_ordering = False
        
    def can_filter(self):
        """
        For SQL returns False is result already fetched
        """
        return True
    
    def set_fields(self, fields):
        self.fields.update(set(fields))
    
    def get_fields(self):
        return list(self.fields)
    
    def clone(self):
        obj = self.__class__(self.model)
        obj.where = Node()
        obj.where = deepcopy(self.where)
        obj.order_by = deepcopy(self.order_by)
        obj.fields = deepcopy(self.fields)
        obj.target_collection_prefix = self.target_collection_prefix
        return obj
    
    def add_q(self, q_object):
        """
        Adds a Q-object to the current filter.

        Can also be used to add anything that has an 'add_to_query()' method.
        See also the method / property 'spec', that operates on the tree structure created in this method,
            kept in self.where
        """
        if hasattr(q_object, 'add_to_query'):
            # Complex custom objects are responsible for adding themselves.
            q_object.add_to_query(self)
        else:
            if self.where and q_object.connector != self.AND and len(q_object) > 1:
                self.where.start_subtree(self.AND)
                subtree = True
            else:
                subtree = False
            connector = self.AND
            for child in q_object.children:
                self.where.start_subtree(connector)
                if isinstance(child, Node):
                    self.add_q(child)
                else:
                    mq = MongoQ(False, child[0],child[1])
                    self.where.add(mq,self.COLON)
                self.where.end_subtree()
                connector = q_object.connector
            if q_object.negated:
                self.where.negate()
            if subtree:
                self.where.end_subtree()

    def get_count(self):
        return self.get_result().count()
    
    def has_results(self):
        return bool(self.get_count())
    
    def get_result(self):
        cursor = self.collection.find(self.spec, fields=self.fields and self._column_name(list(self.fields)) or None)

        sort = self.sort
        
        if sort:
            cursor = cursor.sort(sort)
        
        return cursor
    
    def update(self, values):
        data = {}
        for key, val in values.items():
            data[self._column_name(key)] = fix_value(val)

        self.collection.update(self.spec, {"$set": data})
    
    def delete(self):
        self.collection.remove(self.spec)
    
    @property
    def sort(self):
        output = []
        
        default_ordering = self.model._meta.ordering
        
        if not self.order_by and self.default_ordering and default_ordering:
            order_by = default_ordering
        else:
            order_by = self.order_by
        
        for item in order_by:
            if item.startswith('-'):
                output.append((self._column_name(item[1:]), pymongo.DESCENDING))
            else:
                output.append((self._column_name(item), pymongo.ASCENDING))
                
        return output

    def _process_where_node(self, oq, spec):
        if oq.connector != self.DEFAULT:
            if oq.connector == self.COLON:
                q = oq.children[0]
                column_orig = self._column_name(q._get_field_first_part())
                column = q.getDotNotationFieldName(self.model)
                qspec = q.spec(self.model)

                if not column in spec:
                    spec[column] = qspec
                else:
                    filter = spec[column]
                    if not isinstance(spec[column], dict) or not isinstance(qspec, dict):
                        raise MongoQuerySetExeption('Does not support = and <,>,=<,=> in one query (column:%s)' % column)
                    spec[column].update(qspec)
            elif oq.connector == self.AND:
                r = {}
                spec1 = {}
                for a_item in oq.children:
                    if a_item.connector == self.DEFAULT and len(a_item.children) == 1:
                        a_item = a_item.children[0]
                    if a_item.connector != self.DEFAULT:
                        r.update(self._process_where_node(a_item,spec1))
                spec = r
                if oq.negated:
                    spec = negate_where_clause(spec)
            elif oq.connector == self.OR:
                r = []
                for a_item in oq.children:
                    if a_item.connector != self.DEFAULT:
                        spec1 = {}
                        r.append(self._process_where_node(a_item,spec1))
                spec = self._or_operation_optimization({'$or': r})
                if oq.negated:
                    spec = negate_where_clause(spec)
        return spec


    def _or_operation_optimization(self, spec):
        """
        This method creates a very simple optimization to the case where there is a complete $or where statement,
        where all the items are in a form that can be replaced with in $in statement.
        For example, the following can be optimized:
          {'$or': [{'time_on_site': 10.0}, {'time_on_site': 25.0}, {'time_on_site': 275.0}, {'time_on_site': 148.0}]}
        However, the following CAN NOT be optimized:
          {'$or': [{'time_on_site': 10.0}, {'time_on_site': 25.0}, {'time_on_site': 275.0}, {'visit_count': 12.0}]}
          (because not all parameters are identical)
        Returns the original spec if can't be optimized, or a new $in where statement in the format:
          { x : { $in : [ a, b ] } }
        See also http://www.mongodb.org/display/DOCS/OR+operations+in+query+expressions for more information
        """
        param = None
        values = []
        for item in spec['$or']:
            p = item.keys()
            if len(p)!=1:
                return spec
            if param is None:
                param = p[0]
            if param != p[0]:
                return spec
            if isinstance(item[param], dict):
                return spec
            values.append(item[param])

        res = {param: {'$in': values}}
        return res


    @property
    def spec(self):
        if not self.where:
            return None
        
        spec = {}
        
#        for oq in self.where.children:
#            spec = self._process_where_node(oq, spec)
        spec = self._process_where_node(self.where, spec)

        return spec
    
    @property
    def collection(self):
        return get_collection(self.model,self.target_collection_prefix)
    
    def _prepare_before_insert(self, doc):
        if isinstance(doc, (list, tuple)):
            return [self._prepare_before_insert(d) for d in doc]
        
        data = {}
        
        for name, value in doc.items():
            data[self._column_name(name)] = value

        return data
    
    def insert(self, docs):
        return self.collection.insert(self._prepare_before_insert(docs), safe=True)
