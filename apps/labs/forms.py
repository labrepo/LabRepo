# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

from common.forms import BaseForm
from labs.documents import Lab, LabStorage


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
        document = Lab
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
        if self.instance and self.instance.is_member(self.user):
            if 'investigator' in self.changed_data and self.instance.investigator != data['investigator']:
                self._errors['investigator'] = self.error_class([_('You have not permission change lab\'s investigator')])
                del data['investigator']
        return data


class LabStorageForm(BaseForm):
    """
    Form for create/edit laboratory storages
    """
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        document = LabStorage
        fields = ('type', 'username', 'host', 'password', 'path', 'key_file')


class LabAdminForm(LabBaseForm):

    class Meta:
        document = Lab

    def clean(self):
        data = super(LabAdminForm, self).clean()
        is_test = data.get('is_test')
        labs = self._meta.document.objects.filter(is_test=True)
        if labs and is_test and (labs.count() > 1 or (self.instance and labs[0].pk != self.instance.pk)):
            self._errors['is_test'] = self.error_class(['There was only one test lab'])
        return data
