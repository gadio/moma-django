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
import base64
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.template import RequestContext
from django.utils import timezone
from django.views.generic.simple import direct_to_template
from django.core.context_processors import csrf
from data.forms import QuetionEditForm, DocumentForm
from django.http import HttpResponseRedirect
from data.models import Question
from django.shortcuts import render_to_response
from django import forms
from django.contrib.auth.decorators import login_required

@login_required
def questions_home(request):
    user = request.user
    q_qs = Question.objects.all()
    if 'filter' in request.GET and request.GET['filter'] == 'user':
        q_qs = q_qs.filter(user=user)
    if 'sort' in request.GET and request.GET['sort'] == 'time':
        questions = [(q.date, q) for q in q_qs]
    else:
        questions = [((-len(q.vote_ids), q.date), q) for q in q_qs]
    questions = map(lambda x: x[1], sorted(questions))
    context = {'questions': questions, 'the_user': request.user}
    context.update(csrf(request))
    return render_to_response('question/home.html', context)


@login_required
def questions_search(request):
    user = request.user
    if request.method == 'POST':
        the_user=None
        if User.objects.filter(username=request.POST['search']).count() == 1:
            the_user = User.objects.get(username=request.POST['search'])
        questions = Question.objects.filter(Q(question__iregex=request.POST['search'])|Q(user=the_user)).order_by('date')
        context = {'questions': questions, 'the_user': request.user}
        context.update(csrf(request))
        return render_to_response('question/home.html', context)

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
                return HttpResponseRedirect('/q/media/?q=%s'% nq.id)
            else:
                question = Question.objects.get(id=question_id)
                question.question = txt
                question.save()
                questions = Question.objects.all()
                return HttpResponseRedirect('/q/media/?q=%s'% question.id)
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
def list_question_media(request):
    # Handle file upload
    context = {}
    documents = []

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            docfile = request.FILES['docfile']
            question_id = form.cleaned_data['question_id']

            question = Question.objects.get(id=question_id)
            docfile_name = docfile.name
            docfile_name_changed = docfile_name.replace('.','~^~')
            question.docs.update({docfile_name_changed:docfile.content_type})
            question.image.update({docfile_name_changed +'_url':'/static/display/s_'+docfile_name, docfile_name_changed +'_name': docfile_name, docfile_name_changed +'_content_type':docfile.content_type})
            file_read = docfile.file.read()
            file_data = base64.b64encode(file_read)
            question.image.update({docfile_name_changed +'_data': file_data})
            # question.save()
            nq = Question(
                user = question.user,
                date = question.date,
                question = question.question,
                docs = question.docs,
                image = question.image,
                audio = question.audio,
                other = question.other,
                vote_ids = question.vote_ids,
            )
            question.delete() # todo - there is an update issue here
            nq.save()

            questions = Question.objects.all()
            return render_to_response('question/home.html', {'questions':questions, 'the_user': request.user, 'message': 'Media updated!' })

            # Redirect to the document list after POST
            # return HttpResponseRedirect(reverse('data.views.list_question_media'))
    else:
        if 'q' in request.GET:
            question_id = request.GET['q']
            form = DocumentForm({ 'question_id':question_id,}, hide_condition=True)
            question = Question.objects.get(id=question_id)
            documents = []
            for docname in question.docs:
                file_data = question.image[docname+'_data']
                file_name = question.image[docname+'_name']
                orig_fname = settings.STATIC_ROOT + '/display/' + file_name
                new_fname = settings.STATIC_ROOT + '/display/tn_' + file_name
                _decode_image_to_size(file_data, orig_fname, new_fname, basewidth=128)
                documents.append({'docfile':{'url':question.image[docname +'_url'], 'name':question.image[docname+'_name'], 'thumb':'/static/display/tn_'+question.image[docname+'_name']}})
            context.update({'q': question_id, 'question':question})

    # Load documents for the list page
    # documents = [{'docfile':{'url':'blaaa', 'name':'Bleee'}}]

    context.update( {'documents': documents, 'form': form,})
    context.update(csrf(request))
    context.update({'the_user': request.user})

    return direct_to_template(request, 'question/question_media.html', context)


def _change_image_size(fname_in, fname_out, basewidth=300):
    import PIL
    from PIL import Image

    img = Image.open(fname_in)
    # original_size = img,size[0]
    wpercent = (basewidth/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    img = img.resize((basewidth,hsize), PIL.Image.ANTIALIAS)
    img.save(fname_out)
    new_size = img.size

    # return {'original_size':original_size, 'new_size':new_size, 'percent':wpercent}


def _decode_image_to_size(file_data, orig_fname, new_fname, basewidth):
    import os
    if os.path.exists(new_fname):
        return
    file_decoded_data = base64.b64decode(file_data)
    f = file(orig_fname, 'w')
    f.write(file_decoded_data)
    f.close()
    _change_image_size(orig_fname, new_fname, basewidth=basewidth)


@login_required
def review_question_media(request):
    question_id = request.GET['q']
    question = Question.objects.get(id=question_id)

    documents = {}
    for docname in question.docs.keys():
        file_data = question.image[docname+'_data']
        file_name = question.image[docname+'_name']
        orig_fname = settings.STATIC_ROOT + '/display/' + file_name
        new_fname = settings.STATIC_ROOT + '/display/s_' + file_name
        _decode_image_to_size(file_data, orig_fname, new_fname, basewidth=300)
        documents.update({file_name:'/static/display/s_'+file_name})

    context = {}
    context.update( {'documents': documents, })
    context.update(csrf(request))
    context.update({'the_user': request.user})
    context.update({'question': question})

    return direct_to_template(request, 'question/review_question_media.html', context)


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


