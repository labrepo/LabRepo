# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

from common.forms import BaseForm, SelectFormMixin, CheckOwnerEditMixin
from common.widgets import DateTimeWidget, CKEditorUploadWidget
from experiments.documents import Experiment


class ExperimentForm(SelectFormMixin, CheckOwnerEditMixin, BaseForm):

    class Meta:
        document = Experiment
        fields = ('title', 'owners', 'editors', 'viewers', 'start', 'end', 'description', 'status')

    def __init__(self, *args, **kwargs):
        super(ExperimentForm, self).__init__(*args, **kwargs)
        self.fields['start'] = forms.DateTimeField(label=_('start'), input_formats=('%m/%d/%Y %H:%M',),
                                                   widget=DateTimeWidget(format='%m/%d/%Y %H:%M', attrs={'class': 'form-control'}))
        self.fields['end'] = forms.DateTimeField(label=_('end'), input_formats=('%m/%d/%Y %H:%M',),
                                                 widget=DateTimeWidget(format='%m/%d/%Y %H:%M', attrs={'class': 'form-control'}))
        lab = self.initial['lab']
        self.user = self.initial['user']
        del self.initial['user']
        self.fields['description'].widget = CKEditorUploadWidget(config_name='ckeditor', lab_pk=lab.pk)

    def clean(self):
        data = super(ExperimentForm, self).clean()
        if data.get('start') and data.get('end') and data.get('start') > data.get('end'):
            self._errors['start'] = self.error_class([_('Start date must be less than end date')])
            del data['start']
        return data


class ExperimentUpdateForm(BaseForm):

    class Meta:
        document = Experiment
        fields = ('start', 'end')