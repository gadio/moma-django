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
import bson
from djangotoolbox.fields import ListField, DictField

class MongoIdField(models.CharField, models.AutoField):
    
    def __init__(self, **kwargs):
        kwargs['max_length'] = 24
        kwargs['blank'] = True
        kwargs['primary_key'] = True
        kwargs['db_column'] = '_id'
        kwargs.setdefault('editable', False)
        super(MongoIdField, self).__init__(**kwargs)
        
    def get_internal_type(self):
        return models.CharField.__name__

    def contribute_to_class(self, cls, name):
        assert not cls._meta.has_auto_field, \
          "A model can't have more than one AutoField: %s %s %s; have %s" % \
           (self, cls, name, cls._meta.auto_field)
        super(MongoIdField, self).contribute_to_class(cls, name)
        cls._meta.has_auto_field = True
        cls._meta.auto_field = self
    
    def to_python(self, value):
        if isinstance(value, bson.objectid.ObjectId):
            return value
        
        return bson.objectid.ObjectId(str(value))
    
    def get_prep_lookup(self, lookup_type, value):
        if lookup_type in ('range', 'in'):
            return [self.get_prep_value(v) for v in value]
            
        return self.to_python(value)


class MongoDateTimeField(models.DateTimeField):
    def get_db_prep_value(self, value, connection, prepared=False):
        # Casts dates into the format expected by the backend
        if not prepared:
            value = self.get_prep_value(value)
        return value


class ValuesField(ListField):
    def formfield(self, **kwargs):
        return models.Field.formfield(self, StringListField, **kwargs)

    def _convert(self, func, values, *args, **kwargs):
        if isinstance(values, (list, tuple, set)):
            return self._type(func(value, *args, **kwargs) for value in values)
        if isinstance(values, (str,unicode)):
            split_values = values.replace('[','').replace(']','').replace(' ','').split(',')
            values_lst = [i for i in split_values if len(i)>0]
            return self._type(func(value, *args, **kwargs) for value in values_lst)
        return values


class StringListField(models.CharField):
    def prepare_value(self, value):
        return ', '.join(value)

    def to_python(self, value):
        if not value:
            return []
        return [item.strip() for item in value.split(',')]


class DictionaryField(DictField):
    def _convert(self, func, values, *args, **kwargs):
        if values is None:
            return None
        if isinstance(values, (str, unicode)):
            return eval(values)
        return dict((key, func(value, *args, **kwargs))
            for key, value in values.iteritems())