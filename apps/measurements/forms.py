# -*- coding: utf-8 -*-
from django import forms

from django.forms import CharField

from common.forms import BaseForm
from common.widgets import DateTimeWidget, CKEditorUploadWidget
from .models import Measurement


class MeasurementForm(BaseForm):
    """
    Not used
    """
    def __init__(self, *args, **kwargs):
        lab_pk = kwargs.pop('lab_pk')
        super(MeasurementForm, self).__init__(*args, **kwargs)
        # self.fields['created_at'] = forms.DateTimeField(widget=DateTimeWidget(format='%m/%d/%Y %H:%M'))
        # self.fields['description'].widget = CKEditorUploadWidget(config_name='ckeditor', lab_pk=lab_pk)

    class Meta:
        model = Measurement
        fields = ('table_data', )


class MeasurementDescriptionForm(BaseForm):

    def __init__(self, *args, **kwargs):
        lab_pk = kwargs.pop('lab_pk')
        super(MeasurementDescriptionForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget = CKEditorUploadWidget(config_name='ckeditor', lab_pk=lab_pk)
        self.fields['description'].label = ''

    class Meta:
        model = Measurement
        fields = ('table_data', )


# class MeasurementAdminForm(EmbeddedDocumentForm):
#     # def __init__(self, *args, **kwargs):
#     #     super(MeasurementAdminForm, self).__init__(*args, **kwargs)
#     #     self.fields['created_at'] = forms.DateTimeField(widget=DateTimeWidget(format='%m/%d/%Y %H:%M'))
#
#     def save(self, commit=True):
#         self.instance.save()
#         return super(MeasurementAdminForm, self).save(commit)
#
#     class Meta:
#         document = Measurement
#         fields = ('created_at', 'measurement_type', 'value', 'description')
#         embedded_field_name = 'measurements'


class MeasurementUpdateForm(MeasurementForm):
    comment = CharField(max_length=255, required=False)

#
# class MeasurementTypeForm(BaseForm):
#     def __init__(self, *args, **kwargs):
#         lab_pk = kwargs.pop('lab_pk')
#         super(MeasurementTypeForm, self).__init__(*args, **kwargs)
#         self.fields['description'].widget = CKEditorUploadWidget(config_name='ckeditor', lab_pk=lab_pk)
#
#     class Meta:
#         document = MeasurementType
#         fields = ('description', 'units', 'measurement_type')
