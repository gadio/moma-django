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
from django.http import HttpResponseRedirect
from data.models import Question
from django.shortcuts import render_to_response

from django.contrib.auth.decorators import login_required

@login_required
def questions_home(request):
    user = request.user
    questions = Question.objects.all()
    return render_to_response('question/home.html', {'questions':questions, 'the_user': request.user})

@login_required
def vote(request):
    allowed_votes = 3
    user = request.user

    already_voted=0
    questions = Question.objects.all()
    for question in questions:
        if user.id in question.vote_ids:
            already_voted += 1
        if already_voted >= 3:
            return render_to_response('question/home.html', {'questions':questions, 'the_user': request.user, 'message': 'You can only vote %s times!' % allowed_votes})

    question_id = request.GET['q']
    question = Question.objects.get(id=question_id)
    if user.id not in question.vote_ids:
        question.vote_ids.append(user.id)
        question.save()
    return render_to_response('question/home.html', {'questions':Question.objects.all(), 'the_user': request.user, 'message': 'Voted!!' })



@login_required
def un_vote(request):
    user = request.user
    question_id = request.GET['q']
    question = Question.objects.get(id=question_id)
    if user.id in question.vote_ids:
        question.vote_ids.remove(user.id)
        question.save()
    return render_to_response('question/home.html', {'questions':Question.objects.all(), 'the_user': request.user, 'message': 'Un-voted!!' })
