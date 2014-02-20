#==========================================================================
# Copyright 2012 Lucidel, Inc., 2013 Cloudoscope Inc.
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
from django.contrib.auth.models import User

from django.db import models
from moma_django import MongoModel, post_syncdb_mongo_handler
from moma_django.fields import MongoDateTimeField, DictionaryField, ValuesField



# Enabling South for the non conventional mongo model
#
# add_introspection_rules(
#     [
#         (
#             (MongoIdField, MongoDateTimeField, DictionaryField ),
#             [],
#             {
#                 "max_length":   ["max_length",   {"default": None}],
#                 },
#         ),
#         ],
#     ["^mongo_django.fields.*",])


class Question(MongoModel):
    user = models.ForeignKey(User)
    date = MongoDateTimeField(db_index=True)
    question = models.CharField(max_length=256 )

    image = DictionaryField()
    audio = DictionaryField()
    other = DictionaryField()

    vote_ids = ValuesField(models.IntegerField())


    def __unicode__(self):
        return u'%s[%s %s]' % (self.question, self.date, self.user, )

    class Meta:
        unique_together = ['user', 'question',]
        managed = False

models.signals.post_syncdb.connect(post_syncdb_mongo_handler)

