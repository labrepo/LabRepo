# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

from django.db.models import Q

from common.forms import BaseForm, SelectFormMixin, CheckOwnerEditMixin
from common.widgets import DateTimeWidget, CKEditorUploadWidget
from experiments.models import Experiment
from units.models import Unit


class ExperimentForm(SelectFormMixin, CheckOwnerEditMixin, BaseForm):

    class Meta:
        model = Experiment
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
        model = Experiment
        fields = ('start', 'end')


class UpdateUnitsForm(BaseForm):
    """
    Used to add units to a experiment. TODO: remove model form?
    """
    experiment = forms.ModelChoiceField(queryset=Experiment.objects.none())
    units = forms.ModelMultipleChoiceField(queryset=Unit.objects.none())

    class Meta:
        model = Experiment
        fields = ('experiment',)

    def __init__(self, *args, **kwargs):
        self.lab = kwargs['initial']['lab']
        self.user = kwargs['initial']['user']

        super(UpdateUnitsForm, self).__init__(*args, **kwargs)
        del self.initial['user']
        del self.initial['lab']
        experiment = Experiment.objects.filter(lab=self.lab.pk)
        if not self.lab.is_owner(self.user):
            experiment = experiment.filter((Q(owners__in=[self.user]) | Q(editors__in=[self.user]) | Q(viewers__in=[self.user])))
        self.fields['experiment'].queryset = experiment

        self.fields['units'].queryset = Unit.objects.filter(lab=self.lab, active=True)

        self.fields['units'].widget.attrs['class'] += ' hidden-field'
        self.fields['units'].label = ''
        self.fields['units'].error_messages['required'] = _('You didn\'t select any units.')


class AddUnitToExperimentForm(BaseForm):
    """
    Used to add units to a experiment.
    """
    experiment = forms.ModelChoiceField(queryset=Experiment.objects.none())
    units = forms.ModelMultipleChoiceField(queryset=Unit.objects.none())

    class Meta:
        model = Experiment
        fields = ('experiment',)

    def __init__(self, *args, **kwargs):
        self.lab = kwargs['initial']['lab']
        self.user = kwargs['initial']['user']

        experiment = kwargs['initial']['experiment']
        experiment_qs = Experiment.objects.filter(lab=self.lab.pk)
        if not self.lab.is_owner(self.user):
            experiment_qs = experiment_qs.filter((Q(owners__in=[self.user]) | Q(editors__in=[self.user]) | Q(viewers__in=[self.user])))

        super(AddUnitToExperimentForm, self).__init__(*args, **kwargs)

        self.fields['experiment'].widget = forms.HiddenInput()
        self.fields['experiment'].queryset = experiment_qs
        self.fields['experiment'].initial = experiment.pk
        self.fields['experiment'].label = ''
        self.fields['experiment'].help_text = ''
        self.fields['units'].help_text = ''

        self.fields['units'].queryset = Unit.objects.filter(lab=self.lab, active=True).exclude(experiments=experiment)
        self.fields['units'].label = ''
        self.fields['units'].error_messages['required'] = _('You didn\'t select any units.')
        self.fields['units'].widget.attrs['class'] += ' select2'
        del self.initial['user']
        del self.initial['lab']



