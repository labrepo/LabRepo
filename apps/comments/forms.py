# -*- coding: utf-8 -*-

from django import forms

from comments.documents import Comment
from common.forms import BaseForm
from common.widgets import CKEditorUploadWidget


class CommentForm(BaseForm):

    def __init__(self, *args, **kwargs):
        lab_pk = kwargs.pop('lab_pk')
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['text'].label = ''
        self.fields['text'].widget = CKEditorUploadWidget(config_name='ckeditor', lab_pk=lab_pk)

    object_id = forms.CharField(max_length=255, widget=forms.HiddenInput())

    class Meta:
        document = Comment
        fields = ('text', 'instance_type')
        widgets = {
            'instance_type': forms.HiddenInput(),
        }
