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

from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'moma_example.views.home', name='home'),
    # url(r'^moma_example/', include('moma_example.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # User auth urls
    url(r'^accounts/login/$', 'moma_example.views.login'),
    url(r'^accounts/auth/$', 'moma_example.views.auth_view'),
    url(r'^accounts/logout/$', 'moma_example.views.logout'),
    url(r'^accounts/loggedin/$', 'moma_example.views.loggedin'),
    url(r'^accounts/invalid/$', 'moma_example.views.invalid_login'),
    url(r'^accounts/register/$', 'moma_example.views.register_user'),
    url(r'^accounts/register_success/$', 'moma_example.views.register_success'),
)
