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

from django.db import models
from .queryset import MongoQuerySet

class MongoManager(models.Manager):
    
    def contribute_to_class(self, model, name):
        super(MongoManager, self).contribute_to_class(model, name)
        setattr(model, '_base_manager', getattr(model, '_default_manager'))
        self.using_collection_prefix = None

    def bulk_insert(self, items):
        #n = 10000
        
        #for i in xrange(0, len(items), n):
        #    self.get_query_set().insert(items[i:i+n])
        return self.get_query_set().insert(items)
    
    def _insert(self, values, fields, **kwargs):
        doc = {}
        for field in fields:
            for val in values:
                value = getattr(val, field.attname)
                doc[field.name] = value


        id = self.get_query_set().insert(doc)

        if kwargs.get('return_id'):
            return id
    
    def get_query_set(self):
        res = MongoQuerySet(self.model)
        if not hasattr(self,'using_collection_prefix'):
            self.using_collection_prefix = None
        if self.using_collection_prefix is not None:
            res._using_collection_prefix(self.using_collection_prefix)
        return res
    
    def ensure_index(self, *args, **kwargs):
        return self.get_query_set().ensure_index(*args, **kwargs)
    
    def index_information(self):
        return self.get_query_set().index_information()
    
    def reindex(self):
        return self.get_query_set().reindex()
    
    def values_list(self, *args, **kwargs):
        return self.get_query_set().values_list(*args, **kwargs)
    
    def drop_indexes(self):
        return self.get_query_set().drop_indexes()

    def _setTargetCollectionPrefix(self, using_collection_prefix=None):
        """
        This method enables redirecting the entire model onto another collection.
        Note: this should be used VERY carefully as it will redirect all reading and writing.
        Use using_collection_prefix=None to cancel the redirection.
        E.g. if using_collection_prefix='acme_' and the db name is 'customers', a new db will be used, called 'acme_customers'.
        """
        self.using_collection_prefix = using_collection_prefix
