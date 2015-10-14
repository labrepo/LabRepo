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
        self.fields['text'].widget = CKEditorUploadWidget(config_name='comments', lab_pk=lab_pk)
        self.fields['text'].widget.attrs['id'] = 'comment-{}-{}-{}'.format(self.prefix,
                                                                                  self.initial.get('instance_type'),
                                                                                  self.initial.get('object_id')
                                                                                  ).lower()

    object_id = forms.CharField(max_length=255, widget=forms.HiddenInput())

    class Meta:
        document = Comment
        fields = ('text', 'instance_type')
        widgets = {
            'instance_type': forms.HiddenInput(),
        }
