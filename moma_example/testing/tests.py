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
from django.db.models import Q
from django.test import TestCase
from models import Profile, AnalyticsAccount, TestModel1, TestModel2, TestModel3, UniqueVisit
from datetime import datetime
from django.utils import timezone

class TestMongoQuerySetWithUniqueVisits(TestCase):

    def setUp(self):
        self.user = Profile()
        self.user.username = 'testuser'
        self.user.company_name = 'Test Company'
        self.user.set_password('testuser')
        self.user.save()

        self.acc = AnalyticsAccount(user = self.user)
        self.acc.pk = 10000
        self.acc.name = 'Test'
        self.acc.analytics_id = 'asd324sf456m6n76b5b'
        self.acc.history_fetched = False
        self.acc.save()

        self.other_acc = AnalyticsAccount(user = self.user)
        self.other_acc.pk = 10001
        self.other_acc.name = 'Test1'
        self.other_acc.analytics_id = 'asd324sf456m111111'
        self.other_acc.history_fetched = False
        self.other_acc.save()

        self.list_of_accounts = [self.acc, self.other_acc]

        records = []


        class NumberLong():
            def __init__(self, num):
                self.n = num


        records.append({ "goal_starts" : { }, "time_on_site" : 17, "user_id" : 650825334, "account_id" : NumberLong(5),
                         "campaign" : "(not set)", "location" : { "cr" : "United States", "rg" : "Tennessee",
                                                                  "ct" : "Clarksville" }, "demographics" :
                             { "age" : "GenX (25-44)", "education" : "High School" }, "first_visit_date" :
                             ISODate("2012-08-04T21:18:17Z"), "referral_path" : "(not set)", "source" : "google", "exit_page_path" :
                             "/some-analysis/g1iar-daisy/", "landing_page_path" : "(not set)", "keyword" :
                             "g1iar daisy sparknotes", "date" : ISODate("2012-08-04T00:00:00Z"), "goal_completions" : { },
                         "visit_count" : 1, "visit_id" : "0---30----0---------------650825334.1344115097",
                         "page_views" : 3, "goal_values" : { } })
        records.append({ "goal_starts" : { }, "time_on_site" : 36, "user_id" : 277227593, "account_id" : NumberLong(5),
                         "campaign" : "(not set)", "location" : { "cr" : "United States", "rg" : "Tennessee",
                                                                  "ct" : "Sevierville" }, "demographics" :
                             { "gender" : "Men", "education" : "High School" }, "first_visit_date" :
                             ISODate("2012-08-06T14:46:23Z"), "referral_path" : "(not set)", "source" : "google", "exit_page_path" :
                             "/some-analysis/looking-at-my-ancestors/", "landing_page_path" : "(not set)", "keyword" :
                             "(not provided)", "date" : ISODate("2012-08-06T00:00:00Z"), "goal_completions" : { }, "visit_count" : 1,
                         "visit_id" : "0-2--0-1---1---------------277227593.1344264383", "page_views" : 1,
                         "goal_values" : { } })
        records.append({ "goal_starts" : { }, "time_on_site" : 27, "user_id" : 1429730596, "account_id" : NumberLong(5),
                         "campaign" : "(not set)", "location" : { "cr" : "United States", "rg" : "Virginia",
                                                                  "ct" : "Burke" }, "demographics" :
                             { "gender" : "Men", "age" : "Baby Boomers (45-70)", "education" : "High School" },
                         "first_visit_date" : ISODate("2012-08-06T04:28:22Z"), "referral_path" : "(not set)", "source" :
            "google", "exit_page_path" : "/some-analysis/the_double-blind/", "landing_page_path" : "(not set)",
                         "keyword" : "(not provided)", "date" : ISODate("2012-08-06T00:00:00Z"), "goal_completions" :
                    { }, "visit_count" : 1, "visit_id" : "0-2-90-1--0---------------1429730596.1344227302",
                         "page_views" : 3, "goal_values" : { } })
        records.append({ "goal_starts" : { }, "time_on_site" : 27, "user_id" : 2110905334, "account_id" : NumberLong(5),
                         "campaign" : "(not set)", "location" : { "cr" : "United States", "rg" : "New York",
                                                                  "ct" : "Poughkeepsie" }, "demographics" :
                             { "gender" : "Men", "education" : "High School", "political" : "Democrats" }, "first_visit_date" :
                             ISODate("2012-08-06T18:21:11Z"), "referral_path" : "(not set)", "source" : "yahoo", "exit_page_path" :
                             "/some-analysis/joe-and-bobby/", "landing_page_path" : "(not set)", "keyword" :
                             "book summaries", "date" : ISODate("2012-08-06T00:00:00Z"), "goal_completions" : { },
                         "visit_count" : 1, "visit_id" : "0-0--0-1---------------2110905334.1344277271",
                         "page_views" : 1, "goal_values" : { } })
        records.append({ "goal_starts" : { }, "time_on_site" : 120, "user_id" : 952676001, "account_id" : NumberLong(5),
                         "campaign" : "(not set)", "location" : { "cr" : "United States", "rg" : "Massachusetts",
                                                                  "ct" : "Abington" }, "demographics" :
                             { "age" : "GenX (25-44)", "education" : "High School" },
                         "first_visit_date" : ISODate("2012-08-06T05:53:52Z"), "referral_path" : "(not set)",
                         "source" : "google", "exit_page_path" : "/some-analysis/the-blue-bush/",
                         "landing_page_path" : "(not set)", "keyword" : "(not provided)",
                         "date" : ISODate("2012-08-06T00:00:00Z"), "goal_completions" : { }, "visit_count" : 1,
                         "visit_id" : "0---30---------------952676001.1344232432", "page_views" : 3,
                         "goal_values" : { } })
        records.append({ "goal_starts" : { }, "time_on_site" : 10, "user_id" : 805172613, "account_id" : NumberLong(5),
                         "campaign" : "(not set)", "location" : { "cr" : "United States", "rg" : "New York",
                                                                  "ct" : "Peekskill" }, "demographics" :
                             { "age" : "GenX (25-44)", "education" : "High School" }, "first_visit_date" :
                             ISODate("2012-08-06T16:27:55Z"), "referral_path" : "(not set)", "source" : "bing", "exit_page_path" :
                             "/wikipedia/rama-ii/", "landing_page_path" : "(not set)", "keyword" : "research rama ii", "date" :
                             ISODate("2012-08-06T00:00:00Z"), "goal_completions" : { }, "visit_count" : 2, "visit_id" :
                             "0---30---------------805172613.1344270475", "page_views" : 2, "goal_values" : { } })
        records.append({ "goal_starts" : { }, "time_on_site" : 147, "user_id" : 2060101123, "account_id" : NumberLong(5),
                         "campaign" : "(not set)", "location" : { "cr" : "United States", "rg" : "South Carolina", "ct" :
            "Charleston" }, "demographics" : { "age" : "GenX (25-44)", "education" : "High School" },
                         "first_visit_date" : ISODate("2012-08-06T02:04:05Z"), "referral_path" : "(not set)", "source" :
            "google", "exit_page_path" : "/search", "landing_page_path" : "(not set)", "keyword" :
                             "a short reference", "date" : ISODate("2012-08-06T00:00:00Z"), "goal_completions" : { },
                         "visit_count" : 1, "visit_id" : "0-2-30---------------2060101123.1344218645",
                         "page_views" : 3, "goal_values" : { } })
        records.append({ "goal_starts" : { }, "time_on_site" : 25, "user_id" : 1525231829, "account_id" : NumberLong(5),
                         "campaign" : "(not set)", "location" : { "cr" : "United States", "rg" : "New York", "ct" :
            "Massapequa" }, "demographics" : { "age" : "GenX (25-44)", "education" : "High School" },
                         "first_visit_date" : ISODate("2012-08-05T14:57:17Z"), "referral_path" : "(not set)", "source" :
            "google", "exit_page_path" : "/wikipedia/indian-reservations/", "landing_page_path" : "(not set)", "keyword" :
                             "indian reservations in north america", "date" : ISODate("2012-08-08T00:00:00Z"), "goal_completions" : { },
                         "visit_count" : 2, "visit_id" : "0---30---------------1525231829.1344178637",
                         "page_views" : 2, "goal_values" : { } })
        records.append({ "_id" : ObjectId("502abdabf7f16836f1002847"), "goal_starts" : { }, "time_on_site" : 32,
                         "user_id" : 1322541271, "account_id" : NumberLong(5), "campaign" : "(not set)", "location" :
            { "cr" : "United States", "rg" : "Ohio", "ct" : "Amherst" }, "demographics" : { },
                         "first_visit_date" : ISODate("2012-07-31T12:33:33Z"), "referral_path" : "(not set)", "source" :
            "google", "exit_page_path" : "/some-analysis/the-language-barrier/", "landing_page_path" :
                             "(not set)", "keyword" : "the language barrier", "date" : ISODate("2012-07-31T00:00:00Z"),
                         "goal_completions" : { }, "visit_count" : 1, "visit_id" :
            "false---------------1322541271.1343738013", "page_views" : 2, "goal_values" : { } })
        records.append({ "_id" : ObjectId("502abdabf7f16836f1002848"), "goal_starts" : { }, "time_on_site" : 26,
                         "user_id" : 1044048896, "account_id" : NumberLong(5), "campaign" : "(not set)", "location" :
            { "cr" : "United States", "rg" : "New York", "ct" : "New York" }, "demographics" : { },
                         "first_visit_date" : ISODate("2012-07-31T16:42:23Z"), "referral_path" : "(not set)", "source" :
            "google", "exit_page_path" : "/some-analysis/mercy/", "landing_page_path" : 12, "keyword" :
                             "mercy discussion", "date" : ISODate("2012-07-31T00:00:00Z"), "goal_completions" : { }, "visit_count" :
                1, "visit_id" : "false---------------1044048896.1343752943", "page_views" : 1, "goal_values" :
                             { } })
        records.append({ "_id" : ObjectId("502abdabf7f16836f100284b"), "goal_starts" : { }, "time_on_site" : 38,
                         "user_id" : 184868780, "account_id" : NumberLong(5), "campaign" : "(not set)", "location" :
            { "cr" : "Ireland", "rg" : "Dublin", "ct" : "Dublin" }, "demographics" : { }, "first_visit_date" :
                             ISODate("2012-07-30T14:47:47Z"), "referral_path" : "(not set)", "source" : "google", "exit_page_path" :
                             "/some-analysis/jewelery-cutting/", "landing_page_path" : "(not set)", "keyword" :
                             "practical jewel setting and cutting", "date" : ISODate("2012-07-30T00:00:00Z"), "goal_completions" :
                    { }, "visit_count" : 1, "visit_id" : "false---------------184868780.1343659667",
                         "page_views" : 3, "goal_values" : { } })
        records.append({ "_id" : ObjectId("502abdabf7f16836f100284c"), "goal_starts" : { }, "time_on_site" : 196,
                         "user_id" : 1805411236, "account_id" : NumberLong(5), "campaign" : "(not set)", "location" :
            { "cr" : "India", "rg" : "Kerala", "ct" : "Cochin" }, "demographics" : { }, "first_visit_date" :
                             ISODate("2012-07-30T12:29:05Z"), "referral_path" : "/analysis-nama-ecological-expert/", "source" :
                             "articlemyriad.com", "exit_page_path" : "/some-analysis/the-financial-expert/", "landing_page_path" :
                             "/analysis-nama-ecological-expert/", "keyword" : "(not set)", "date" : ISODate("2012-07-30T00:00:00Z"),
                         "goal_completions" : { }, "visit_count" : 1, "visit_id" :
            "false---------------1805411236.1343651345", "page_views" : 11, "goal_values" : { } })
        records.append({ "_id" : ObjectId("502abdabf7f16836f100284d"), "goal_starts" : { }, "time_on_site" : 11,
                         "user_id" : 169596409, "account_id" : NumberLong(5), "campaign" : "(not set)", "location" :
            { "cr" : "United States", "rg" : "Pennsylvania", "ct" : "Willow Grove" }, "demographics" :
                             { "education" : "College" }, "first_visit_date" : ISODate("2012-07-31T12:16:26Z"), "referral_path" :
                             "(not set)", "source" : "yahoo", "exit_page_path" : "/some-analysis/the-maincoon-cat/", "landing_page_path" :
                             "(not set)", "keyword" : "the maincoon cat", "date" : ISODate("2012-07-31T00:00:00Z"),
                         "goal_completions" : { }, "visit_count" : 1, "visit_id" :
                "0----2---------------169596409.1343736986", "page_views" : 1, "goal_values" : { } })
        records.append({ "_id" : ObjectId("502abdabf7f16836f100284e"), "goal_starts" : { }, "time_on_site" : 275,
                         "user_id" : 157428922, "account_id" : NumberLong(5), "campaign" : "(not set)", "location" :
            { "cr" : "United States", "rg" : "Ohio", "ct" : "Chillicothe" }, "demographics" : { },
                         "first_visit_date" : ISODate("2012-08-01T00:20:25Z"), "referral_path" : "(not set)", "source" :
            "google", "exit_page_path" : "/some-analysis/a-bend-in-the-road/", "landing_page_path" :
                             21, "keyword" : "(not provided)", "date" : ISODate("2012-07-31T00:00:00Z"), "goal_completions" :
                    { }, "visit_count" : 1, "visit_id" : "false---------------157428922.1343780425",
                         "page_views" : 1, "goal_values" : { } })
        records.append({ "_id" : ObjectId("502abdabf7f16836f100284f"), "goal_starts" : { }, "time_on_site" : 148,
                         "user_id" : 1419573589, "account_id" : NumberLong(5), "campaign" : "(not set)", "location" :
            { "cr" : "South Africa", "rg" : "Western Cape", "ct" : "Cape Town" }, "demographics" : { },
                         "first_visit_date" : ISODate("2012-07-31T19:02:10Z"), "referral_path" : "(not set)", "source" :
            "google", "exit_page_path" : "/some-analysis/the-american-eagle/", "landing_page_path" :
                             "(not set)", "keyword" : "american eagle habitats", "date" : ISODate("2012-07-31T00:00:00Z"),
                         "goal_completions" : { }, "visit_count" : 1, "visit_id" :
                "false---------------1419573589.1343761330", "page_views" : 2, "goal_values" : { } })
        records.append({ "_id" : ObjectId("502abdabf7f16836f1002850"), "goal_starts" : { }, "time_on_site" : 54,
                         "user_id" : 553686581, "account_id" : NumberLong(5), "campaign" : "(not set)", "location" :
            { "cr" : "United States", "rg" : "California", "ct" : "Whittier" }, "demographics" :
                             { "age" : "GenX (25-44)", "education" : "College" }, "first_visit_date" :
                             ISODate("2012-07-31T17:39:12Z"), "referral_path" : "(not set)", "source" : "yahoo", "exit_page_path" :
                             "/search", "landing_page_path" : "(not set)", "keyword" : "book summaries", "date" :
                             ISODate("2012-07-31T00:00:00Z"), "goal_completions" : { }, "visit_count" : 1, "visit_id" :
                             "06--32----0---------------553686581.1343756352", "page_views" : 4, "goal_values" : { } })
        records.append({ "_id" : ObjectId("502abdabf7f16836f1002852"), "goal_starts" : { }, "time_on_site" : 105,
                         "user_id" : 804661250, "account_id" : NumberLong(5), "campaign" : "(not set)", "location" :
            { "cr" : "United States", "rg" : "Missouri", "ct" : "St Louis" }, "demographics" :
                             { "education" : "Grad School" }, "first_visit_date" : ISODate("2012-07-30T20:56:39Z"),
                         "referral_path" : "(not set)", "source" : "google", "exit_page_path" :
            "/some-analysis/people-of-australia/", "landing_page_path" : "(not set)", "keyword" :
                             "people of australia study guide", "date" : ISODate("2012-07-30T00:00:00Z"),
                         "goal_completions" : { }, "visit_count" : 1, "visit_id" :
            "0----3---------------804661250.1343681799", "page_views" : 2, "goal_values" : { } })
        records.append({ "_id" : ObjectId("502abdabf7f16836f1002857"), "goal_starts" : { }, "time_on_site" : 68,
                         "user_id" : 1587838983, "account_id" : NumberLong(5), "campaign" : "(not set)", "location" :
            { "cr" : "United States", "rg" : "California", "ct" : "San Francisco" }, "demographics" : { },
                         "first_visit_date" : ISODate("2012-07-30T07:55:27Z"), "referral_path" : "(not set)", "source" :
            "google", "exit_page_path" : "/wikipedia/riders-of-the-west/", "landing_page_path" : "(not set)",
                         "keyword" : "(not provided)", "date" : ISODate("2012-07-30T00:00:00Z"), "goal_completions" :
                    { }, "visit_count" : 1, "visit_id" : "false---------------1587838983.1343634927",
                         "page_views" : 2, "goal_values" : { } })
        records.append({ "_id" : ObjectId("502abdabf7f16836f1002859"), "goal_starts" : { }, "time_on_site" : 10,
                         "user_id" : 876838713, "account_id" : NumberLong(5), "campaign" : "(not set)", "location" :
            { "cr" : "United States", "rg" : "Michigan", "ct" : "Hart" }, "demographics" : { },
                         "first_visit_date" : ISODate("2012-07-30T11:47:30Z"), "referral_path" : "(not set)", "source" :
            "google", "exit_page_path" : "/some-analysis/the-cover-story/", "landing_page_path" :
                             "(not set)", "keyword" : "cover story notes", "date" : ISODate("2012-07-30T00:00:00Z"),
                         "goal_completions" : { }, "visit_count" : 1, "visit_id" :
            "false---------------876838713.1343648850", "page_views" : 1, "goal_values" : { } })
        records.append({ "_id" : ObjectId("502abdabf7f16836f100285a"), "goal_starts" : { }, "time_on_site" : 290,
                         "user_id" : 1154449631, "account_id" : NumberLong(5), "campaign" : "(not set)", "location" :
            { "cr" : "United States", "rg" : "California", "ct" : "Pasadena" }, "demographics" : { },
                         "first_visit_date" : ISODate("2012-07-30T17:10:06Z"), "referral_path" : "(not set)", "source" :
            "google", "exit_page_path" : "/some-analysis/lion-king/", "landing_page_path" : "(not set)",
                         "keyword" : "wikipedia lion king", "date" : ISODate("2012-07-30T00:00:00Z"),
                         "goal_completions" : { }, "visit_count" : 1, "visit_id" :
            "false---------------1154449631.1343668206", "page_views" : 3, "goal_values" : { } })

        self.the_records = records
        for i in self.the_records:
            i.pop('account_id')
            if '_id' in i:
                i.pop('_id')
            i['account'] = self.acc.pk

        UniqueVisit.objects.filter(account__in=self.list_of_accounts).delete()
        self.assertEqual(UniqueVisit.objects.filter(account__in=self.list_of_accounts).count(), 0)

        UniqueVisit.objects.bulk_insert(self.the_records)

        self.assertEqual(UniqueVisit.objects.filter(account__in=self.list_of_accounts).count(), len(self.the_records))


    def test_insert(self):
        """
        Taken from here https://github.com/django/django/blob/master/tests/modeltests/basic/tests.py
        """
        UniqueVisit.objects.filter(account__in=self.list_of_accounts).delete()
        self.assertEqual(UniqueVisit.objects.filter(account__in=self.list_of_accounts).count(), 0)

        UniqueVisit.objects.bulk_insert(self.the_records)

        self.assertEqual(UniqueVisit.objects.filter(account__in=self.list_of_accounts).count(), len(self.the_records))


    def test_simple_account_reference_query(self):
        qs = UniqueVisit.objects.filter(account = self.acc.pk)
        num = 0
        self.assertEqual( qs.query.spec, dict(
            {'account_id': 10000}
        ))
        for i in self.the_records:
            num += 1
        self.assertEqual(qs.count(), num)


    def test_simple_time_reference_query(self):
        qs = UniqueVisit.objects.filter(first_visit_date__lte =ISODate("2012-07-30T12:29:05Z"))
        num = 0
        self.assertEqual( qs.query.spec, dict({'first_visit_date': {'$lte': datetime(2012, 7, 30, 12, 29, 5, tzinfo=timezone.utc)}}))
        for i in self.the_records:
            if i['first_visit_date'] <= ISODate("2012-07-30T12:29:05Z"):
                num += 1
        self.assertEqual(qs.count(), num)


    def test_simple_time_reference_query_multiple_terms2(self):
        qs = UniqueVisit.objects.filter(first_visit_date__lte =ISODate("2012-07-30T12:29:05Z"),time_on_site__gt =10)
        num = 0
        self.assertEqual( qs.query.spec, dict({'time_on_site': {'$gt': 10.0}, 'first_visit_date':
            {'$lte': datetime(2012, 7, 30, 12, 29, 5, tzinfo=timezone.utc)}}))
        for i in self.the_records:
            if i['first_visit_date'] <= ISODate("2012-07-30T12:29:05Z") and i['time_on_site'] > 10:
                num += 1
        self.assertEqual(qs.count(), num)


    def test_simple_time_reference_query_multiple_terms3(self):
        qs = UniqueVisit.objects.filter(first_visit_date__lte =ISODate("2012-07-30T12:29:05Z"),time_on_site__gt =10,
                                        page_views__gt =2)
        num = 0
        self.assertEqual( qs.query.spec, dict({'time_on_site': {'$gt': 10.0}, 'page_views': {'$gt': 2},
                                               'first_visit_date': {'$lte': datetime(2012, 7, 30, 12, 29, 5, tzinfo=timezone.utc)}}))
        for i in self.the_records:
            if i['first_visit_date'] <= ISODate("2012-07-30T12:29:05Z") and \
                            i['time_on_site'] > 10 and \
                            i['page_views'] > 2:
                num += 1
        self.assertEqual(qs.count(), num)


    def test_simple_time_reference_query_with_Q(self):
        qs = UniqueVisit.objects.filter(Q(first_visit_date__lte =ISODate("2012-07-30T12:29:05Z")))
        num = 0
        self.assertEqual( qs.query.spec, dict({'first_visit_date': {'$lte': datetime(2012, 7, 30, 12, 29, 5, tzinfo=timezone.utc)}}))
        for i in self.the_records:
            if i['first_visit_date'] <= ISODate("2012-07-30T12:29:05Z"):
                num += 1
        self.assertEqual(qs.count(), num)


    def test_simple_time_reference_query_with_Q_2_AND(self):
        qs = UniqueVisit.objects.filter(Q(first_visit_date__lte =ISODate("2012-07-30T12:29:05Z"))&Q(time_on_site__gt =10))
        num = 0
        self.assertEqual( qs.query.spec, dict({'time_on_site': {'$gt':10.0}, 'first_visit_date':
            {'$lte': datetime(2012, 7, 30, 12, 29, 5, tzinfo=timezone.utc)}}))
        for i in self.the_records:
            if i['first_visit_date'] <= ISODate("2012-07-30T12:29:05Z") and i['time_on_site']>10:
                num += 1
        self.assertEqual(qs.count(), num)


    def test_simple_time_reference_query_with_Q_2_OR(self):
        qs = UniqueVisit.objects.filter(Q(first_visit_date =ISODate("2012-07-30T12:29:05Z"))|Q(time_on_site =10))
        num = 0
        self.assertEqual( qs.query.spec, dict(
            {'$or': [{'first_visit_date': datetime(2012, 7, 30, 12, 29, 5, tzinfo=timezone.utc)}, {'time_on_site': 10.0}]}
        ))
        for i in self.the_records:
            if i['first_visit_date']  ==  ISODate("2012-07-30T12:29:05Z") or i['time_on_site'] == 10:
                num += 1
        self.assertEqual(qs.count(), num)


    def test_simple_time_reference_query_with_Q_3_OR_with_same_param(self):
        qs = UniqueVisit.objects.filter(Q(time_on_site =10)|Q(time_on_site =25)|Q(time_on_site =275))
        num = 0
        self.assertEqual( qs.query.spec, dict(
            # old non optimized   {'$or': [{'time_on_site': 10.0}, {'time_on_site': 25.0}, {'time_on_site': 275.0}]}
            {'time_on_site': {'$in': [10.0, 25.0, 275.0]}}
        ))
        for i in self.the_records:
            if i['time_on_site'] == 25 or i['time_on_site'] == 10 or i['time_on_site'] == 275:
                num += 1
        qs = qs.filter(account__in=self.list_of_accounts)
        self.assertEqual(qs.count(), num)

    def test_query_with_in_opr(self):
        qs = UniqueVisit.objects.filter(time_on_site__in=[10, 25, 274])
        num = 0
        self.assertEqual( qs.query.spec, dict(
            {'time_on_site': {'$in': [10.0, 25.0, 274.0]}}
        ))
        for i in self.the_records:
            if i['time_on_site'] == 25 or i['time_on_site'] == 10 or i['time_on_site'] == 274:
                num += 1
        qs = qs.filter(account__in=self.list_of_accounts)
        self.assertEqual(qs.count(), num)

    def test_simple_time_reference_query_with_Q_4_OR_with_different_param(self):
        qs = UniqueVisit.objects.filter(Q(time_on_site =10)|Q(time_on_site =25)|Q(time_on_site =275)|Q(source = 'bing'))
        num = 0
        for i in self.the_records:
            if i['time_on_site']  ==  25 or i['time_on_site'] == 10 or i['time_on_site'] == 275:
                num += 1
        qs2 = qs.filter(account__in=self.list_of_accounts)
        self.assertEqual(qs2.count(), num)
        self.assertEqual( qs.query.spec, dict(
            {'$or': [{'time_on_site': 10.0}, {'time_on_site': 25.0}, {'time_on_site': 275.0}, {'source': 'bing'}]}
        ))

    def test_simple_time_reference_query_with_Q_4_OR_with_same_param_different_operation(self):
        qs = UniqueVisit.objects.filter(Q(time_on_site = 10)|Q(time_on_site = 25)|Q(time_on_site = 275) | Q(time_on_site__gt = 7))
        num = 0
        self.assertEqual( qs.query.spec, dict(
            {'$or': [{'time_on_site': 10.0}, {'time_on_site': 25.0}, {'time_on_site': 275.0},
                     {'time_on_site': {'$gt': 7.0}}]}
        ))
        for i in self.the_records:
            if i['time_on_site'] == 25 or i['time_on_site'] == 10 or i['time_on_site'] == 275 or i['time_on_site']>7:
                num += 1
        qs = qs.filter(account__in=self.list_of_accounts)
        self.assertEqual(qs.count(), num)

    def test_query_with_Q_AND_OR_combination(self):
        qs = UniqueVisit.objects.filter(Q(time_on_site =10)|Q(time_on_site =25)|Q(time_on_site =275)&Q(source = 'bing'))
        num = 0
        self.assertEqual( qs.query.spec, dict(
            {'$or': [{'time_on_site': 10.0}, {'time_on_site': 25.0}, {'time_on_site': 275.0, 'source': 'bing'}]}
        ))
        for i in self.the_records:
            if i['time_on_site'] == 25 or i['time_on_site'] == 10 or (i['time_on_site'] == 275 and i['source'] ==  'bing'):
                num += 1
        qs = qs.filter(account__in=self.list_of_accounts)
        self.assertEqual(qs.count(), num)


    def test_query_with_Q_OR_tree_combination(self):
        qs = UniqueVisit.objects.filter(Q(time_on_site =10)|(Q(time_on_site =25)|Q(time_on_site =275))|Q(time_on_site =148))
        num = 0
        self.assertEqual( qs.query.spec, dict(
            # old, non optimized:  {'$or': [{'time_on_site': 10.0}, {'time_on_site': 25.0}, {'time_on_site': 275.0}, {'time_on_site': 148.0}]}
            {'time_on_site': {'$in': [10.0, 25.0, 275.0, 148.0]}}
        ))
        for i in self.the_records:
            if i['time_on_site'] == 25 or i['time_on_site'] == 10 or (i['time_on_site'] == 275 or i['time_on_site'] == 148):
                num += 1
        qs = qs.filter(account__in=self.list_of_accounts)
        self.assertEqual(qs.count(), num)


    def test_simple_time_reference_query_with_Q_3_OR(self):
        qs = UniqueVisit.objects.filter(Q(time_on_site = 10) | Q(first_visit_date = ISODate("2012-07-30T12:29:05Z"))|
                                        Q(visit_count__lte = 2))
        num = 0
        self.assertEqual( qs.query.spec, dict(
            {'$or': [{'time_on_site': 10.0}, {'first_visit_date': datetime(2012, 7, 30, 12, 29, 5, tzinfo=timezone.utc)},
                     {'visit_count': {'$lte': 2}}]}
        ))
        for i in self.the_records:
            if i['time_on_site'] == 10 or i['first_visit_date'] == ISODate("2012-07-30T12:29:05Z") or i['visit_count']<=2:
                num += 1
        self.assertEqual(qs.count(), num)


    def test_simple_time_reference_query_with_Q_N_OR_regex_build(self):
        lst = [ 'facebook', 'yahoo', '.com']
        kwargs = {'source__regex': 'blog'}
        the_q = Q(**kwargs)
        for item in lst:
            kwargs = {'source__regex': item}
            the_q |= Q(**kwargs)
        qs = UniqueVisit.objects.filter(the_q)
        num = 0
        self.assertEqual( qs.query.spec, dict(
            {'$or': [{'source': {'$regex': 'blog'}}, {'source': {'$regex': 'facebook'}},
                     {'source': {'$regex': 'yahoo'}}, {'source': {'$regex': '.com'}}]}
        ))
        for i in self.the_records:
            matches = [i['source'].find(word)>=0 for word in lst]
            if sum(matches)>0:
                num += 1
        self.assertEqual(qs.count(), num)


    def test_simple_time_reference_query_with_Q_N_OR_iregex_build(self):
        lst = [ 'facebook', 'yahoo', '.com']
        kwargs = {'source__regex': 'blog'}
        q=Q(**kwargs)
        for item in lst:
            kwargs = {'source__iregex': item}
            q |= Q(**kwargs)
        qs = UniqueVisit.objects.filter(q)
        num = 0
        self.assertEqual( qs.query.spec, dict(
            {'$or': [{'source': {'$regex': 'blog'}}, {'source': {'$options': 'i', '$regex': 'facebook'}},
                     {'source': {'$options': 'i', '$regex': 'yahoo'}}, {'source': {'$options': 'i', '$regex': '.com'}}]}
        ))
        for i in self.the_records:
            matches = [i['source'].find(word)>=0 for word in lst]
            if sum(matches)>0:
                num += 1
        self.assertEqual(qs.count(), num)


    def test_simple_time_reference_query_with_Q_N_OR_regex_build_negate(self):
        lst = [ 'facebook', 'yahoo', '.com']
        kwargs = {'source__regex': 'blog'}
        q=Q(**kwargs)
        for item in lst:
            kwargs = {'source__regex': item}
            q |= Q(**kwargs)
        qs = UniqueVisit.objects.filter(~q)
        num = 0
        self.assertEqual( qs.query.spec, dict(
            {'$nor': [{'source': {'$regex': 'blog'}}, {'source': {'$regex': 'facebook'}},
                      {'source': {'$regex': 'yahoo'}}, {'source': {'$regex': '.com'}}]}
        ))
        for i in self.the_records:
            matches = [i['source'].find(word)>=0 for word in lst]
            if not sum(matches)>0:
                num += 1
        qs = qs.filter(account__in=self.list_of_accounts)
        self.assertEqual(qs.count(), num)

    def test_simple_time_reference_query_with_equal_opr_negate(self):
        qs = UniqueVisit.objects.filter(~Q(first_visit_date =ISODate("2012-07-30T12:29:05Z")))
        num = 0
        self.assertEqual( qs.query.spec, dict({'first_visit_date': {'$ne': datetime(2012, 7, 30, 12, 29, 5, tzinfo=timezone.utc)}}))
        for i in self.the_records:
            if not(i['first_visit_date']  ==  ISODate("2012-07-30T12:29:05Z")):
                num += 1
        qs = qs.filter(account__in=self.list_of_accounts)
        self.assertEqual(qs.count(), num)

    def test_query_with_equal_opr_DOUBLE_negated(self):
        qs = UniqueVisit.objects.filter(~(~Q(first_visit_date =ISODate("2012-07-30T12:29:05Z"))))
        num = 0
        self.assertEqual( qs.query.spec, dict({'first_visit_date': datetime(2012, 7, 30, 12, 29, 5, tzinfo=timezone.utc)}))
        for i in self.the_records:
            if not(not(i['first_visit_date']  ==  ISODate("2012-07-30T12:29:05Z"))):
                num += 1
        self.assertEqual(qs.count(), num)

    def test_simple_time_reference_query_with_Q_lte_opr_negate(self):
        qs = UniqueVisit.objects.filter(~Q(first_visit_date__lte =ISODate("2012-07-30T12:29:05Z")))
        num = 0
        self.assertEqual( qs.query.spec, dict({'first_visit_date': {'$gt': datetime(2012, 7, 30, 12, 29, 5, tzinfo=timezone.utc)}}))
        for i in self.the_records:
            if not(i['first_visit_date'] <= ISODate("2012-07-30T12:29:05Z")):
                num += 1
        qs = qs.filter(account__in=self.list_of_accounts)
        self.assertEqual(qs.count(), num)

    def test_simple_time_reference_query_with_Q_gte_opr_negate(self):
        qs = UniqueVisit.objects.filter(~Q(first_visit_date__gte =ISODate("2012-07-30T12:29:05Z")))
        num = 0
        self.assertEqual( qs.query.spec, dict({'first_visit_date': {'$lt': datetime(2012, 7, 30, 12, 29, 5, tzinfo=timezone.utc)}}))
        for i in self.the_records:
            if not(i['first_visit_date'] >= ISODate("2012-07-30T12:29:05Z")):
                num += 1
        self.assertEqual(qs.count(), num)

    def test_query_with_in_opr_negate(self):
        qs = UniqueVisit.objects.filter(~Q(time_on_site__in=[10, 25, 275]))
        num = 0
        self.assertEqual( qs.query.spec, dict(
            {'time_on_site': {'$nin': [10.0, 25.0, 275.0]}}
        ))
        for i in self.the_records:
            if not(i['time_on_site'] == 25 or i['time_on_site'] == 10 or i['time_on_site'] == 275):
                num += 1
        self.assertEqual(qs.count(), num)

    def test_simple_time_reference_query_with_Q_3_AND_negated(self):
        qs = UniqueVisit.objects.filter(~(Q(time_on_site =10)&(~Q(first_visit_date =ISODate("2012-07-30T12:29:05Z")))&
                                          Q(visit_count__lte =2)))
        num = 0
        self.assertEqual( qs.query.spec, dict(
            {'$or': [{'time_on_site': {'$ne': 10.0}}, {'visit_count': {'$gt': 2}},
                     {'first_visit_date': datetime(2012, 7, 30, 12, 29, 5, tzinfo=timezone.utc)}]}
        ))
        for i in self.the_records:
            if not(i['time_on_site'] == 10 and
                       not i['first_visit_date'] == ISODate("2012-07-30T12:29:05Z") and
                           i['visit_count']<=2):
                num += 1
        qs = qs.filter(account__in=self.list_of_accounts)
        self.assertEqual(qs.count(), num)


    def test_simple_time_reference_query_with_Q_3_OR_negated(self):
        qs = UniqueVisit.objects.filter(~(Q(time_on_site =10)|Q(first_visit_date =ISODate("2012-07-30T12:29:05Z"))|
                                          Q(visit_count__lte =2)))
        num = 0
        self.assertEqual( qs.query.spec, dict(
            {'$nor': [{'time_on_site': 10.0}, {'first_visit_date': datetime(2012, 7, 30, 12, 29, 5, tzinfo=timezone.utc)},
                      {'visit_count': {'$lte': 2}}]}
        ))
        for i in self.the_records:
            if not(i['time_on_site'] == 10 or
                           i['first_visit_date'] == ISODate("2012-07-30T12:29:05Z") or
                           i['visit_count']<=2):
                num += 1
        qs = qs.filter(account__in=self.list_of_accounts)
        self.assertEqual(qs.count(), num)



    def test_dot_notation_query(self):
        qs = UniqueVisit.objects.filter(location__rg__exact ="New York")
        num = 0
        self.assertEqual( qs.query.spec, dict(
            {'location.rg': 'New York'}
        ))
        for i in self.the_records:
            if 'rg' in i['location'] and i['location']['rg']  ==  'New York':
                num += 1
        self.assertEqual(qs.count(), num)

    def test_exists_query(self):
        qs = UniqueVisit.objects.filter(demographics__age__exists ="true")
        num = 0
        self.assertEqual( qs.query.spec, dict(
            {'demographics.age': {'$exists': 'true'}}
        ))
        for i in self.the_records:
            if 'age' in i['demographics']:
                num += 1
        self.assertEqual(qs.count(), num)

    def test_bson_type_query(self):
        qs = UniqueVisit.objects.filter(landing_page_path__type = int)
        num = 0
        self.assertEqual( qs.query.spec, dict(
            {'landing_page_path': {'$type': 16}}
        ))
        for i in self.the_records:
            if type( i['landing_page_path']) == int:
                num += 1
        self.assertEqual(qs.count(), num)

        qs = UniqueVisit.objects.filter(landing_page_path__type = str)
        num = 0
        self.assertEqual( qs.query.spec, dict(
            {'landing_page_path': {'$type': 2}}
        ))
        for i in self.the_records:
            if type( i['landing_page_path']) == str:
                num += 1
        self.assertEqual(qs.count(), num)


class TestMongoORMInfrastructure(TestCase):
    def setUp(self):
        self.user = Profile()
        self.user.username = 'testuser'
        self.user.company_name = 'Test Company'
        self.user.set_password('testuser')
        self.user.save()

        self.acc = AnalyticsAccount(user = self.user)
        self.acc.pk = 10000
        self.acc.name = 'Test'
        self.acc.analytics_id = 'asd324sf456m6n76b5b'
        self.acc.history_fetched = False
        self.acc.save()

        self.other_acc = AnalyticsAccount(user = self.user)
        self.other_acc.pk = 10001
        self.other_acc.name = 'Test1'
        self.other_acc.analytics_id = 'asd324sf456m111111'
        self.other_acc.history_fetched = False
        self.other_acc.save()

        self.list_of_accounts=[self.acc, self.other_acc]

        records = []

        records.append({"start_date":datetime(2005, 7, 28), "values":[], "some_id":2,})
        records.append({"start_date":datetime(2005, 8, 28), "values":[], "some_id":2,})
        records.append({"start_date":datetime(2005, 8, 28), "values":[], "some_id":3,})

        self.the_records = records

        TestModel1.objects.all().delete()
        self.assertEqual(TestModel1.objects.all().count(), 0)
        TestModel2.objects.all().delete()
        self.assertEqual(TestModel2.objects.all().count(), 0)
        TestModel3.objects.all().delete()
        self.assertEqual(TestModel3.objects.all().count(), 0)

        TestModel1.objects.bulk_insert(self.the_records)

        self.assertEqual(TestModel1.objects.all().count(), len(self.the_records))

        tm1a = TestModel1.objects.get(start_date = datetime(2005, 7, 28, tzinfo=timezone.utc), some_id =2)

        # Creating on object from TestModel2 referencing an object from TestModel1
        tm2a = TestModel2(ref1= tm1a, start_date = datetime(2005, 8, 12), values=[1, 3], some_id =12)
        tm2a.save()

        self.assertEqual(TestModel2.objects.all().count(), 1)

        # Creating on object from TestModel3 wo reference
        tm3a = TestModel3(start_date = datetime(2005, 8, 12), values=[1, 3], some_id =12)
        tm3a.save()
        self.assertEqual(TestModel3.objects.all().count(), 1)

        # Creating on object from TestModel3 with reference
        tm1b = TestModel1.objects.get(start_date = datetime(2005, 8, 28, tzinfo=timezone.utc), some_id =3)
        tm2b = TestModel2(ref1= tm1b, start_date = datetime(2005, 8, 13), values=[1, 3], some_id =13)
        tm2b.save()
        tm3b = TestModel3( ref2= tm2b, start_date = datetime(2005, 8, 12), values=[1, 3], some_id =14)
        tm3b.save()
        self.assertEqual(TestModel3.objects.all().count(), 2)
        self.assertEqual(TestModel2.objects.all().count(), 2)


    def test_delete_non_referenced_object(self):
        pre1 = TestModel1.objects.all().count()
        self.assertNotEqual(pre1, 0)
        pre2 = TestModel2.objects.all().count()
        self.assertNotEqual(pre2, 0)
        pre3 = TestModel3.objects.all().count()
        self.assertNotEqual(pre3, 0)
        TestModel1.objects.filter(start_date = datetime(2005, 8, 28, tzinfo=timezone.utc), some_id =3).delete()

        self.assertEqual(TestModel1.objects.all().count(), pre1-1)
        self.assertEqual(pre2, TestModel2.objects.all().count())
        self.assertEqual(pre3, TestModel3.objects.all().count())


    def test_delete_referenced_object_m1_m2_with_cascade(self):
        pre1 = TestModel1.objects.all().count()
        self.assertNotEqual(pre1, 0)
        pre2 = TestModel2.objects.all().count()
        self.assertNotEqual(pre2, 0)
        pre3 = TestModel3.objects.all().count()
        self.assertNotEqual(pre3, 0)
        tm1o =  TestModel1.objects.get(start_date = datetime(2005, 7, 28, tzinfo=timezone.utc), some_id =2)
        tm1o.delete()

        self.assertEqual(TestModel1.objects.all().count(), pre1-1)
        self.assertEqual(TestModel2.objects.all().count(), pre2-1)
        self.assertEqual(pre3, TestModel3.objects.all().count())

    def test_delete_of_queryset(self):
        pre1 = TestModel1.objects.all().count()
        self.assertNotEqual(pre1, 0)
        pre2 = TestModel2.objects.all().count()
        self.assertNotEqual(pre2, 0)
        pre3 = TestModel3.objects.all().count()
        self.assertNotEqual(pre3, 0)
        TestModel1.objects.filter(start_date = datetime(2005, 7, 28, tzinfo=timezone.utc), some_id =2).delete()

        self.assertEqual(TestModel1.objects.all().count(), pre1-1)
        # Delete through the filter will behave differently and will not follow a cascade relationship
        # (see different behaviour in test_delete_referenced_object_m1_m2)
        self.assertEqual(TestModel2.objects.all().count(), pre2)
        self.assertEqual(pre3, TestModel3.objects.all().count())


    def test_delete_cascade_2nd_level(self):
        pre1 = TestModel1.objects.all().count()
        self.assertNotEqual(pre1, 0)
        pre2 = TestModel2.objects.all().count()
        self.assertNotEqual(pre2, 0)
        pre3 = TestModel3.objects.all().count()
        self.assertNotEqual(pre3, 0)
        tm1o =  TestModel1.objects.get(start_date = datetime(2005, 8, 28, tzinfo=timezone.utc), some_id =3)
        tm1o.delete()

        self.assertEqual(TestModel1.objects.all().count(), pre1-1)
        self.assertEqual(TestModel2.objects.all().count(), pre2-1)
        self.assertEqual(TestModel3.objects.all().count(), pre3-1)


def ISODate(timestr):
    res = datetime.strptime(timestr, "%Y-%m-%dT%H:%M:%SZ")
    res = res.replace(tzinfo=timezone.utc)
    return res

def ObjectId(st):
    return st

