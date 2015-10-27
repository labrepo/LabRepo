# -*- coding: utf-8 -*-
from mongodbforms import CharField, embeddedformset_factory, EmbeddedDocumentFormSet

from django import forms
from common.forms import BaseForm
from common.widgets import CKEditorUploadWidget
from .documents import Unit
from measurements.documents import Measurement
from experiments.documents import Experiment
from labs.documents import Lab
from tags.documents import Tag
from measurements.forms import MeasurementAdminForm


class UnitForm(BaseForm):
    def __init__(self, *args, **kwargs):
        kwargs.pop('lab_pk')
        super(UnitForm, self).__init__(*args, **kwargs)

    class Meta:
        document = Unit
        exclude = ('lab', 'active', 'measurements')


class UnitPopupForm(BaseForm):
    """
    Handle pop up unit form
    """
    def __init__(self, *args, **kwargs):
        lab_pk = kwargs.pop('lab_pk')
        exp_pk = kwargs.pop('exp_pk')
        lab = Lab.objects.get(pk=lab_pk)
        experiment = Experiment.objects.get(pk=exp_pk)

        super(UnitPopupForm, self).__init__(*args, **kwargs)

        self.fields['experiments'].widget = forms.HiddenInput()
        self.fields['experiments'].initial = experiment
        self.fields['parent'].queryset = Unit.objects.filter(lab=lab, active=True)
        self.fields['tags'].queryset = Tag.objects.filter(lab=lab)
        # self.fields['description'].widget = CKEditorUploadWidget(config_name='ckeditor', lab_pk=lab_pk,
        #                                                          attrs={'id': 'unit_create_description_field'})
        self.fields['description'].widget.attrs['class'] += ' summernote '

    class Meta:
        document = Unit
        exclude = ('lab', 'active', 'measurements')


class UnitUpdateForm(UnitForm):
    comment = CharField(label='Change reasons', max_length=255, required=False)


class UnitTabForm(BaseForm):
    """
    Form is used on the unit tab on the experiment detail page
    """
    def __init__(self, *args, **kwargs):
        lab_pk = kwargs.pop('lab_pk')
        lab = Lab.objects.get(pk=lab_pk)
        super(UnitTabForm, self).__init__(*args, **kwargs)
        # self.fields['description'].widget = CKEditorUploadWidget(config_name='ckeditor', lab_pk=lab_pk,
        #                                                          attrs={'id': 'unit_description_field'})
                                                                 # FIX CKEDITOR MULTIPLE INSTANCES
        self.fields['description'].label = ''
        self.fields['description'].widget.attrs['class'] += ' summernote '
        self.fields['sample'].widget = forms.TextInput()
        self.fields['parent'].queryset = Unit.objects.filter(lab=lab, active=True)

    class Meta:
        document = Unit
        fields = ('description', 'sample', 'parent')


class UnitEmbeddedDocumentFormSet(EmbeddedDocumentFormSet):
    def __init__(self, data=None, files=None, save_as_new=False, prefix=None, queryset=[], parent_document=None,
                 **kwargs):
        if 'instance' in kwargs:
            parent_document = kwargs.pop('instance')
        super(UnitEmbeddedDocumentFormSet, self).__init__(data, files, save_as_new, prefix, queryset, parent_document,
                                                          **kwargs)

    def save_object(self, form):
        if not hasattr(self, 'changed_objects'):
            self.changed_objects = []
        if not hasattr(self, 'deleted_objects'):
            self.deleted_objects = []
        if not hasattr(self, 'new_objects'):
            self.new_objects = []
        obj = super(UnitEmbeddedDocumentFormSet, self).save_object(form)
        if form.cleaned_data.get("DELETE", False):
            self.deleted_objects.append(obj)
        elif form.instance:
            self.changed_objects.append((obj, form.changed_data))
        else:
            self.new_objects.append(obj)
        return obj


MeasurementFormSet = embeddedformset_factory(Measurement, parent_document=Unit, form=MeasurementAdminForm,
                                             formset=UnitEmbeddedDocumentFormSet)