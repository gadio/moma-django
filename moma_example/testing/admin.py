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

from django.contrib import admin
from models import UniqueVisit, TestModel1, TestModel2, TestModel3, AnalyticsAccount, Profile


class UniqueVisitAdmin(admin.ModelAdmin):
    list_display = ['account', 'date', 'visit_count', 'source', 'referral_path', 'keyword', 'campaign', 'landing_page_path', 'exit_page_path',
                    'user_id', 'time_on_site', 'page_views', 'first_visit_date', 'location', 'demographics', 'goal_values', 'goal_starts', 'goal_completions']
    list_filter = ['account', 'date', ]


class TestModel1Admin(admin.ModelAdmin):
    list_display = ['id', 'start_date', 'some_id', 'values',]

class TestModel2Admin(admin.ModelAdmin):
    list_display = ['id', 'start_date', 'some_id', 'values',]

class TestModel3Admin(admin.ModelAdmin):
    list_display = ['id', 'start_date', 'some_id', 'values',]

class AnalyticsAccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_on', ]


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'company_name' ]

admin.site.register(UniqueVisit, UniqueVisitAdmin)
admin.site.register(TestModel1, TestModel1Admin)
admin.site.register(TestModel2, TestModel2Admin)
admin.site.register(TestModel3, TestModel3Admin)
admin.site.register(AnalyticsAccount, AnalyticsAccountAdmin)
admin.site.register(Profile, ProfileAdmin)
