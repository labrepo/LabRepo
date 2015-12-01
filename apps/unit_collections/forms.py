# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

from django.db.models import Q

from unit_collections.documents import Collection
from common.forms import BaseForm, SelectFormMixin, CheckOwnerEditMixin, CheckUnitMixin


class CollectionForm(SelectFormMixin, CheckUnitMixin, CheckOwnerEditMixin, BaseForm):

    class Meta:
        model = Collection
        fields = ('title', 'units', 'owners', 'editors', 'viewers', 'description')

    def __init__(self, *args, **kwargs):
        self.lab = kwargs['initial']['lab']
        self.user = kwargs['initial']['user']
        super(CollectionForm, self).__init__(*args, **kwargs)
        del self.initial['user']

    def clean(self):
        cleaned_data = super(CollectionForm, self).clean()
        if not self.initial['lab'].is_owner(self.user):
            units = []
            for unit in cleaned_data.get('units', []):
                for experiment in unit.experiments:
                    if not experiment.is_experiment_assistant(self.user):
                        if not unit in units:
                            units.append(unit.__unicode__())
            if units:
                raise forms.ValidationError(_(u'You have not permission to add this units {} in your '
                                              u'collection'.format(','.join(units))))
        return cleaned_data


class UpdateUnitsCollectionForm(CheckUnitMixin, BaseForm):
    collection = forms.ModelChoiceField(queryset=Collection.objects.none())

    class Meta:
        model = Collection
        fields = ('units',)

    def __init__(self, *args, **kwargs):
        self.lab = kwargs['initial']['lab']
        self.user = kwargs['initial']['user']

        super(UpdateUnitsCollectionForm, self).__init__(*args, **kwargs)
        del self.initial['user']
        del self.initial['lab']
        collections = Collection.objects.filter(lab=self.lab.pk)
        if not self.lab.is_owner(self.user):
            collections = collections.filter((Q(owners__in=[self.user]) | Q(editors__in=[self.user]) |
                                              Q(viewers__in=[self.user]) | Q(units__in=self.fields['units'].queryset)))
        self.fields['collection'].queryset = collections
        self.fields['units'].widget.attrs['class'] += ' hidden-field'
        self.fields['units'].label = ''
        self.fields['units'].error_messages['required'] = _('You didn\'t select any units.')
