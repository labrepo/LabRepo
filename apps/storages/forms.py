# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

from djangular.forms import NgModelFormMixin, NgFormValidationMixin, NgModelForm

from common.forms import  FormMixin
from .models import LabStorage


class LabStorageForm(NgFormValidationMixin, FormMixin, NgModelFormMixin, NgModelForm):
    """
    Form for create/edit laboratory storages
    """
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    key_file = forms.FileField(required=False)

    class Meta:
        model = LabStorage
        fields = ('type', 'readonly', 'username', 'host', 'password', 'path', 'folder_name', 'key_file')

    def __init__(self, *args, **kwargs):
        super(LabStorageForm, self).__init__(*args, **kwargs)
        self.fields['readonly'].widget = forms.CheckboxInput()
        self.fields['readonly'].widget.attrs['class'] = self.fields['readonly'].widget.attrs.get('class', '') + ' checkbox'
        self.initial['type'] = 1  # SFTP
        if self.instance.pk and not self.instance.folder_name:
            self.initial['folder_name'] = self.instance.get_folder_name()
