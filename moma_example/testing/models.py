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


class Profile(User):
    company_name = models.CharField(max_length=200)

    @property
    def accounts(self):
        if self.is_superuser:
            return AnalyticsAccount.objects.all()
        else:
            return self.analyticsaccount_set.all()



class AnalyticsAccount(models.Model):
    user = models.ForeignKey(Profile)
    name = models.CharField(max_length=500)

    website_url = models.CharField(max_length=1000, null=True)


    created_on = models.DateTimeField(null=True, help_text='Time registered', blank=True, default=None)

    class Meta:
        ordering = ['name',]



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



class UniqueVisit(MongoModel):
    account = models.ForeignKey('testing.AnalyticsAccount')
    date = MongoDateTimeField(db_index=True)
    visit_count = models.IntegerField()
    source = models.CharField(max_length=64 )
    referral_path = models.CharField(max_length=256 )
    keyword = models.CharField(max_length=256 )
    landing_page_path = models.CharField(max_length=256 )
    exit_page_path = models.CharField(max_length=256 )
    demographics_and_id = models.CharField(max_length=64 )
    time_on_site = models.FloatField(max_length=64 )
    page_views = models.IntegerField()
    campaign = models.CharField(max_length=64 )
    visit_id = models.CharField(max_length=64 )

    location = DictionaryField(item_field=models.CharField(max_length=64))
    demographics = DictionaryField(models.CharField(max_length=64))

    user_id = models.IntegerField()
    first_visit_date = MongoDateTimeField()

    goal_values = DictionaryField(models.FloatField())
    goal_starts = DictionaryField(models.IntegerField())
    goal_completions = DictionaryField(models.IntegerField())


    def __unicode__(self):
        return u'%s[%s %s %s]' % (self.account, self.date, self.visit_count, self.demographics_and_id)

    class Meta:
        unique_together = ['account', 'date', 'visit_count', 'visit_id']
        managed = False



#---------------------------------------
# TEST MODELS
# The following models are used only for testing purposes

class TestModel1(MongoModel):
    start_date = MongoDateTimeField()
    values = ValuesField(models.FloatField())
    some_id = models.IntegerField()

    def __unicode__(self):
        return u'TM1 %s[%s]' % (self.some_id, self.start_date)

    class Meta:
        unique_together = ['start_date', 'some_id', ]
        managed = False

class TestModel2(MongoModel):
    ref1 = models.ForeignKey('testing.TestModel1')
    start_date = MongoDateTimeField()
    values = ValuesField(models.FloatField())
    some_id = models.IntegerField()

    def __unicode__(self):
        return u'TM2 %s[%s]' % (self.some_id, self.start_date)

    class Meta:
        unique_together = ['start_date', 'some_id', ]
        managed = False

class TestModel3(MongoModel):
    ref1 = models.ForeignKey('testing.TestModel1')
    ref2 = models.ForeignKey('testing.TestModel2')
    start_date = MongoDateTimeField()
    values = ValuesField(models.FloatField())
    some_id = models.IntegerField()

    def __unicode__(self):
        return u'TM2 %s[%s]' % (self.some_id, self.start_date)

    class Meta:
        unique_together = ['start_date', 'some_id', ]
        managed = False


class TstBook(MongoModel):
    name = models.CharField(max_length=64)
    publish_date = MongoDateTimeField()
    author = models.ForeignKey('testing.TstAuthor')


class TstAuthor(MongoModel):
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)




models.signals.post_syncdb.connect(post_syncdb_mongo_handler)

# End: TEST MODELS
#---------------------------------------
