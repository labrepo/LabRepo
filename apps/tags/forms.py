# coding: utf-8
import json

from django import forms
from django.forms import HiddenInput, TextInput, Textarea
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from .documents import Tag
from common.forms import BaseForm


class DictWidget(HiddenInput):

    def render(self, name, value, attrs=None):
        value = json.dumps(value)

        html = u"""
        <div id="div_id_{0}" class="form-group">
          <label for="id_{0}" class="control-label">{1}</label>
          {2}
          <div id="json-field" class="form-group"></div>
        </div>
        """.format(name, _(name).capitalize(), super(DictWidget, self).render(name, value, attrs))

        return mark_safe(html)


class ColorWidget(TextInput):

    def render(self, name, value, attrs=None):
        html = u"""
        <div class="input-group input-colorpicker" data-color={}>
          <div class="input-group-addon">
            <i></i>
          </div>
          {}
        </div>
        """.format(value or "#00c0ef", super(ColorWidget, self).render(name, value, attrs))

        return mark_safe(html)


class TagBaseForm(BaseForm):
    def clean_params(self):
        data = self.cleaned_data['params']
        try:
            data = json.loads(data)
        except ValueError:
            raise forms.ValidationError(_(u"Must be a dict"))
        return data


class TagForm(TagBaseForm):
    def __init__(self, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)
        self.lab_pk = self.initial.pop('lab_pk')
        self.fields['parent'].queryset = self.instance._meta.document.objects.filter(lab=self.lab_pk)
        if kwargs.get('instance'):
            self.fields['parent'].queryset = self.fields['parent'].queryset.filter(
                pk__nin=[child.pk for child in kwargs.get('instance').get_children()])
        # self.fields['params'].initial = {"": ""}
        # self.fields['params'].label = _(u'params')

    class Meta:
        document = Tag
        widgets = {
            'details': Textarea(attrs={'rows': 1}),
            # 'params': DictWidget(),
            'color': ColorWidget()
        }
        # fields = ('details', 'parent', 'color', 'params',)
        fields = ('details', 'parent', )

    def clean(self):
        data = super(TagBaseForm, self).clean()
        color = data.get('color')
        parent = data.get('parent')
        if not color:
            data['color'] = parent.color if parent else '#000000'
        if data.get('details') and self.lab_pk:
            # Check on unique details, lab and parent, don't work as unique_with with parent.required=false
            tags = Tag.objects.filter(details=data.get('details'), lab=self.lab_pk, parent=parent)
            if tags and (self.instance and not filter(lambda tag: tag.pk == self.instance.pk, tags)):
                self.errors['details'] = [_(u'Must be unique inside lab and parent')]
        return data


class TagAdminForm(TagBaseForm):
    class Meta:
        document = Tag
