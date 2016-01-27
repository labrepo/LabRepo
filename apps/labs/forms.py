# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

from common.forms import BaseForm
from .models import Lab


class LabBaseForm(BaseForm):

    def clean(self):
        data = super(LabBaseForm, self).clean()
        if 'investigator' in data:
            if 'members' in data and set(data['investigator']) & set(data['members']):
                self._errors["members"] = self.error_class(['field value \'investigator\' should not interfere with the field values \'members\''])
                del data['members']
            if 'guests' in data and set(data['investigator']) & set(data['guests']):
                self._errors["guests"] = self.error_class(['field value \'investigator\' should not interfere with the field values \'guests\''])
                del data['guests']
        return data


class LabForm(LabBaseForm):
    """
    Form for create/edit laboratory
    """
    class Meta:
        model = Lab
        fields = ('name', 'investigator', 'members', 'guests')

    def __init__(self, *args, **kwargs):
        super(LabForm, self).__init__(*args, **kwargs)
        self.fields['investigator'].widget.attrs['data-dependent'] = 'members,guests'
        self.fields['members'].widget.attrs['data-dependent'] = 'investigator,guests'
        self.fields['guests'].widget.attrs['data-dependent'] = 'members,investigator'
        self.user = self.initial['user']
        del self.initial['user']

    def clean(self):
        data = super(LabForm, self).clean()

        if self.instance.id and self.instance.is_member(self.user):
            if 'investigator' in self.changed_data and self.instance.investigator != data['investigator']:
                self._errors['investigator'] = self.error_class([_('You have not permission change lab\'s investigator')])
                del data['investigator']
        return data
