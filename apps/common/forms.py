from django import forms
from django.utils.translation import ugettext_lazy as _

from units.models import Unit
from profiles.models import LabUser


class FormMixin(object):
    """Add bootstrap3 and select2 classes for form widgets."""
    def __init__(self, *args, **kwargs):
        super(FormMixin, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = self.fields[field].widget.attrs.get('class', '') + ' form-control'
            if getattr(self.fields[field], 'choices', None):
                self.fields[field].widget.attrs['class'] += ' select2'


class SelectFormMixin(object):
    """Helper class for user select fields"""

    def __init__(self, *args, **kwargs):
        """Set user select fields querysets."""
        super(SelectFormMixin, self).__init__(*args, **kwargs)
        self.fields['owners'].widget.attrs['data-dependent'] = 'editors,viewers'
        self.fields['editors'].widget.attrs['data-dependent'] = 'owners,viewers'
        self.fields['viewers'].widget.attrs['data-dependent'] = 'editors,owners'
        lab = self.initial['lab']
        people = [obj.pk for obj in list(lab.investigator.all()) + list(lab.members.all()) + list(lab.guests.all())]
        self.fields['owners'].queryset = LabUser.objects.filter(pk__in=people)
        self.fields['editors'].queryset = LabUser.objects.filter(pk__in=people)
        self.fields['viewers'].queryset = LabUser.objects.filter(pk__in=people)

    def clean(self):
        """Owners, editors,viewers fields must not intersect."""
        data = super(SelectFormMixin, self).clean()
        if set(data.get('owners', [])) & set(data.get('editors', [])):
            self._errors["members"] = self.error_class([_('Field value \'owners\' should not interfere with the field values \'editors\'')])
            del data['editors']
        if set(data.get('owners', [])) & set(data.get('viewers', [])):
            self._errors["viewers"] = self.error_class([_('Field value \'owners\' should not interfere with the field values \'viewers\'')])
            del data['viewers']
        return data


class CheckOwnerEditMixin(object):
    """Check permissions."""
    def clean(self):
        data = super(CheckOwnerEditMixin, self).clean()
        if self.instance.pk and self.instance.is_editor(self.user):
            if 'owners' in self.changed_data and self.instance.owners != data['owners']:
                self._errors['owners'] = self.error_class([_('You have not permission change owners')])
                del data['owners']
        return data


class CheckUnitMixin(object):
    def __init__(self, *args, **kwargs):
        """Set unit fields queryset."""
        super(CheckUnitMixin, self).__init__(*args, **kwargs)
        units = []
        unit_queryset = Unit.objects.filter(lab=self.lab.pk, active=True)
        for unit in unit_queryset:
            if unit.is_assistant(self.user):
                units.append(unit.pk)
        self.fields['units'].queryset = unit_queryset.filter(pk__in=units)


class BaseForm(FormMixin, forms.ModelForm):
    pass
