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

import data
from django.conf.urls import patterns, include, url
from django.contrib import admin
from moma_example import settings

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'moma_example.views.home', name='home'),

    url(r'^admin/', include(admin.site.urls)),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),

    # User auth urls
    url(r'^accounts/login/$', 'moma_example.views.login', name='login'),
    url(r'^accounts/auth/$', 'moma_example.views.auth_view'),
    url(r'^accounts/logout/$', 'moma_example.views.logout', name='logout'),
    url(r'^accounts/loggedin/$', 'moma_example.views.loggedin'),
    url(r'^accounts/invalid/$', 'moma_example.views.invalid_login'),
    url(r'^accounts/register/$', 'moma_example.views.register_user', name='register'),
    url(r'^accounts/register_success/$', 'moma_example.views.register_success'),

    url(r'^q/home/$', 'data.views.questions_home', name='questions_home'),
    url(r'^q/edit/$', 'data.views.questions_edit'),
    url(r'^q/vote/$', 'data.views.vote'),
    url(r'^q/un_vote/$', 'data.views.un_vote'),
    url(r'^q/media/$', 'data.views.list_question_media', name='list_question_media'),
)
