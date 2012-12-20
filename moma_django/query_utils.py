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

from types import DictType
from .exceptions import MongoQuerySetExeption
from datetime import datetime, date

def fix_value(value):

    if isinstance(value, datetime):
        return value

    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)

    return value

class MongoQ(object):
    COLON = ":"
    NOT = "$ne"
    NE = "$ne"
    GT = "$gt"
    GTE = "$gte"
    LT = "$lt"
    LTE = "$lte"
    IN = "$in"
    NIN = "$nin"
    OR = "$or"
    NOR = "$nor"
    AND = "$and"
    REGEX = "$regex"
    IREGEX = "$regex"
    BSON_TYPE = "$type"
    EXISTS = "$exists"

    lookups = {
        'pk': None,
        'id': None,
        'not': NOT,
        'gt': GT,
        'gte': GTE,
        'lt': LT,
        'lte': LTE,
        'exact': None,
        'in': IN,
        'regex': REGEX,
        'iregex': IREGEX,
        'type' : BSON_TYPE,
        'exists' : EXISTS,
        }

    additional_options = {
        'iregex' : {'$options': 'i'}
    }

    negate_lookup = {
        COLON : NE,
        NE : COLON,
        GT : LTE,
        LTE : GT,
        GTE : LT,
        LT : GTE,
        IN : NIN,
        NIN : IN,
        OR : NOR,
        NOR : OR,
    }

    BSON_TYPES = {
        float : 1,
        str: 2,
        object: 3,
        list: 4,
        bool: 8,
        date: 9,
        datetime: 9,
        None: 10,
        int: 16,
        }

    def __init__(self, negate, filter, value):
        self.negate = negate
        self.filter = filter
        self._value = value
        self._dotFieldNotation = False

    def __deepcopy__(self, memodict):
        q = self.__class__(self.negate, self.filter, self._value)
        return q

    def _get_field_first_part(self):
        params = self.filter.split('__')
        name = params[0]
        return name

    def getDotNotationFieldName(self, model):
        lookup, params = self._analyze_field_lookups(model)
        field = self.getModelField(self.field, model)
        name = field.column
        if self._dotFieldNotation:
            name += '.'+params[1]
        return name

    @property
    def field(self):
        params = self.filter.split('__')
        name = params[0]
        return name

    def construct_spec(self, negate, filter, value, additional_options):
        if filter and filter != self.COLON:
            spec = {filter: value}
            if negate:
                spec = {self.negate_lookup[filter]: value}
            if additional_options:
                spec.update(additional_options)
        else:
            if negate:
                spec = {self.NE: value}
            else:
                spec = value
        return spec

    def _analyze_field_lookups(self, model):
        params = self.filter.split('__')
        if len(params) > 3:
            raise MongoQuerySetExeption('Does not support related objects filtering. Only be related field.')
        elif len(params) == 3:
            meta_field = model._meta.get_field(params[0])
            rel = meta_field.rel
            #this is field that saved as FK in MongoModel so we can filter by this field
            if rel:
                if params[1] == rel.field_name:
                    lookup = params[2]
                else:
                    raise MongoQuerySetExeption('Does not support related objects filtering. Only be related field.')
            elif meta_field._type is DictType:
                lookup = params[2]
                self._dotFieldNotation = True
            else:
                raise MongoQuerySetExeption('No related fields or dict.')
        elif len(params) == 2:
            lookup = params[1]
            if lookup in ('pk', 'id'): #hotfix. should check `rel` attribute of field
                lookup = 'exact'
        else:
            lookup = 'exact'
        return lookup, params

    def getModelField(self, field_name, model):
        if field_name == 'pk':
            field = model._meta.pk
        else:
            field = model._meta.get_field(field_name)
        return field

    def spec(self, model):
        lookup, params = self._analyze_field_lookups(model)

        if lookup not in self.lookups:
            raise MongoQuerySetExeption('Does not support "%s" lookup' % lookup)

        filter = None

        filter = self.lookups[lookup]

        field_name = self._get_field_first_part()
        field = self.getModelField(field_name, model)

        if lookup in self.lookups and self.lookups[lookup]  == self.EXISTS:
            value = self._value
        elif lookup in self.lookups and self.lookups[lookup]  == self.BSON_TYPE:
            value = self.BSON_TYPES[self._value]
        else:
            value = fix_value(field.get_prep_lookup(lookup, self._value))

        additional_options = {}
        if lookup in self.additional_options:
            additional_options = self.additional_options[lookup]

        spec = self.construct_spec(self.negate, filter, value, additional_options)

        return spec


def negate_where_clause(spec):
    res = spec
    if not isinstance(spec, dict):
        return res
    assert isinstance(spec, dict)

    operation = MongoQ.AND

    if len(spec) != 1:
        # original operation is AND. Using de-morgan, not(a AND b) ==> not(a) OR not(b)
        new_operation = MongoQ.OR
        or_items = []
        for k, v in spec.items():
            or_items.append(negate_where_clause({k:v}))
        res = {new_operation : or_items}
        return res

    assert len(spec.keys()) == 1

    field = spec.keys()[0]
    val = spec[field]

    if isinstance(val, dict):
        operation = val.keys()[0]
        val = val[operation]
    elif isinstance(val, list):
        operation = spec.keys()[0]
    else:
        operation = MongoQ.COLON

    new_operation = MongoQ.negate_lookup[operation]

    if new_operation == MongoQ.COLON:
        res = {field : val}
    elif new_operation in [MongoQ.OR, MongoQ.NOR]:
        res = {new_operation : val}
    else:
        res = {field : {new_operation:val}}

    return res
