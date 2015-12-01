# -*- coding: utf-8 -*-

from django import forms

from comments.models import Comment
from common.forms import BaseForm


class CommentForm(BaseForm):

    def __init__(self, *args, **kwargs):
        lab_pk = kwargs.pop('lab_pk')
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['text'].label = ''

        self.fields['text'].widget.attrs['id'] = 'comment-{}-{}-{}'.format(self.prefix,
                                                                                  self.initial.get('instance_type'),
                                                                                  self.initial.get('object_id')
                                                                                  ).lower()
        self.fields['text'].widget.attrs['class'] += ' summernote '

    object_id = forms.CharField(max_length=255, widget=forms.HiddenInput())
    instance_type = forms.CharField(max_length=255, widget=forms.HiddenInput())

    class Meta:
        model = Comment
        fields = ('text', )
        widgets = {
            'instance_type': forms.HiddenInput(),
        }
