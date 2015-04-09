from mongodbforms import DocumentForm
from mongoengine.django.auth import User
from django.utils.translation import ugettext_lazy as _
from units.documents import Unit


class FormMixin(object):

    def __init__(self, *args, **kwargs):
        super(FormMixin, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = self.fields[field].widget.attrs.get('class', '') + ' form-control'
            if getattr(self.fields[field], 'choices', None):
                self.fields[field].widget.attrs['class'] += ' select2'


class SelectFormMixin(object):
    def __init__(self, *args, **kwargs):
        super(SelectFormMixin, self).__init__(*args, **kwargs)
        self.fields['owners'].widget.attrs['data-dependent'] = 'editors,viewers'
        self.fields['editors'].widget.attrs['data-dependent'] = 'owners,viewers'
        self.fields['viewers'].widget.attrs['data-dependent'] = 'editors,owners'
        lab = self.initial['lab']
        people = [obj.pk for obj in lab.investigator + lab.members + lab.guests]
        self.fields['owners'].queryset = User.objects.filter(pk__in=people)
        self.fields['editors'].queryset = User.objects.filter(pk__in=people)
        self.fields['viewers'].queryset = User.objects.filter(pk__in=people)

    def clean(self):
        data = super(SelectFormMixin, self).clean()
        if set(data.get('owners', [])) & set(data.get('editors', [])):
            self._errors["members"] = self.error_class([_('Field value \'owners\' should not interfere with the field values \'editors\'')])
            del data['editors']
        if set(data.get('owners', [])) & set(data.get('viewers', [])):
            self._errors["viewers"] = self.error_class([_('Field value \'owners\' should not interfere with the field values \'viewers\'')])
            del data['viewers']
        return data


class CheckOwnerEditMixin(object):
    def clean(self):
        data = super(CheckOwnerEditMixin, self).clean()
        if self.instance and self.instance.is_editor(self.user):
            if 'owners' in self.changed_data and self.instance.owners != data['owners']:
                self._errors['owners'] = self.error_class([_('You have not permission change owners')])
                del data['owners']
        return data


class CheckUnitMixin(object):
    def __init__(self, *args, **kwargs):
        super(CheckUnitMixin, self).__init__(*args, **kwargs)
        units = []
        unit_queryset = Unit.objects.filter(lab=self.lab.pk, active=True)
        for unit in unit_queryset:
            if unit.is_assistant(self.user):
                units.append(unit.pk)
        self.fields['units'].queryset = unit_queryset.filter(pk__in=units)


class BaseForm(FormMixin, DocumentForm):
    def _post_clean(self):
        self._meta._dont_save = []
        super(BaseForm, self)._post_clean()

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        if not isinstance(self.instance, self._meta.document):
            self.instance = self._meta.document()
