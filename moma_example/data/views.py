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
from django.utils import timezone
from django.views.generic.simple import direct_to_template
from django.core.context_processors import csrf
from data.forms import QuetionEditForm
from django.http import HttpResponseRedirect
from data.models import Question
from django.shortcuts import render_to_response
from django import forms
from django.contrib.auth.decorators import login_required

@login_required
def questions_home(request):
    user = request.user
    questions = Question.objects.all()
    return render_to_response('question/home.html', {'questions':questions, 'the_user': request.user})

@login_required
def questions_edit(request):
    context = {}
    form = QuetionEditForm(hide_condition=True)

    if request.method == 'POST':
        form= QuetionEditForm(request.POST, hide_condition=True)

        if form.is_valid():
            # form.save()
            txt = form.cleaned_data['question_txt']
            question_id = form.cleaned_data['question_id']

            if question_id == '':
                nq = Question(
                    user = request.user,
                    date = timezone.now(),
                    question = txt
                )
                nq.save()
                questions = Question.objects.all()
                return render_to_response('question/home.html', {'questions':questions, 'the_user': request.user, 'message': 'Quetion added!' })
            else:
                question = Question.objects.get(id=question_id)
                question.question = txt
                question.save()
                questions = Question.objects.all()
                return render_to_response('question/home.html', {'questions':questions, 'the_user': request.user, 'message': 'Quetion updated!' })
        else:
            args = {}
            args.update(csrf(request))
            args['form'] = form
            return render_to_response('question/question_form.html', args)
    else:
        if 'q' in request.GET:
            question_id = request.GET['q']
            question = Question.objects.get(id=question_id)
            form = QuetionEditForm({'question_txt':question.question, 'question_id':question_id, }, hide_condition=True)
            context.update({'q': question_id})

    context.update({'form': form})
    context.update(csrf(request))


    return direct_to_template(request, 'question/question_form.html', context)



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
            return render_to_response('question/home.html', {'questions':questions, 'the_user': request.user, 'message': 'You can only vote %s times!' % allowed_votes, 'msg_err':True})

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
