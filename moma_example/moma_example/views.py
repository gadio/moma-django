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

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.core.context_processors import csrf
from django.contrib.auth.forms import UserCreationForm


def home(request):
    if request.user.is_anonymous():
        return HttpResponseRedirect('/accounts/login/')
    else:
        return HttpResponseRedirect('/q/home/')


def login(request):
    c= {}
    c.update(csrf(request))
    return render_to_response('login.html', c)

def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect('/accounts/loggedin')
    else:
        return HttpResponseRedirect('/accounts/invalid')

def loggedin(request):
    # return render_to_response('loggedin.html', {'full_name': request.user.username, 'the_user': request.user})
    return HttpResponseRedirect('/q/home')

def invalid_login(request):
    return render_to_response('invalid_login.html', {'the_user': request.user})

def logout(request):
    auth.logout(request)
    return render_to_response('logout.html', { 'the_user': request.user})

def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/register_success')
        else:
            args = {}
            args.update(csrf(request))
            args['form'] = form
            args['the_user'] = request.user
            return render_to_response('register.html', args)

    args = {}
    args.update(csrf(request))
    args['form'] = UserCreationForm()
    args['the_user'] = request.user

    return render_to_response('register.html', args)

def register_success(request):
    return render_to_response('register_success.html')