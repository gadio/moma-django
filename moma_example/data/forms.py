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
from django import forms
from django.forms import HiddenInput


class QuetionEditForm(forms.Form):
    question_txt = forms.CharField(required=True, label="question_txt", widget=forms.Textarea())
    question_id = forms.CharField(required=False, label="question id",
                                 widget = forms.TextInput(attrs={'type': 'hidden',}))

    def __init__(self, *args, **kwargs):
        from django.forms.widgets import HiddenInput
        hide_condition = kwargs.pop('hide_condition',None)
        super(forms.Form, self).__init__(*args, **kwargs)
        if hide_condition:
            self.fields['question_id'].widget = HiddenInput()
