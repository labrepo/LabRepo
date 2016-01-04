import re

from django import forms
from django.utils.translation import gettext_lazy as _


class SimpleSearchForm(forms.Form):
    q = forms.CharField(label='', widget=forms.TextInput(attrs={'type': 'search', 'placeholder': _('Search'), 'class': 'form-control'}), help_text='')


class SearchForm(forms.Form):
    COMMENT = (
        ('text', _('text')),
        ('init_user.email', _('init user.email')),
    )
    EXPERIMENT = (
        ('title', _('title')),
        ('description', _('description')),
        ('owners.email', _('owners.email')),
        ('editors.email', _('editors.email')),
        ('viewers.email', _('viewers.email')),
    )
    UNIT = (
        ('sample', _('sample')),
        ('tags.details', _('tags.details')),
        ('tags.params', _('tags.params')),
    )
    PROFILE = (
        ('email', _('email')),
        ('first_name', _('first name')),
        ('last_name', _('last name')),
    )

    q = forms.CharField(label='', widget=forms.TextInput(attrs={'type': 'search', 'placeholder': _('Search'), 'class': 'form-control'}), help_text='')
    comment = forms.CharField(label=_('comment'), required=False, widget=forms.Select(choices=COMMENT, attrs={'class': 'search-components'}))
    experiment = forms.CharField(label=_('experiment'), required=False, widget=forms.Select(choices=EXPERIMENT, attrs={'class': 'search-components'}))
    unit = forms.CharField(label=_('unit'), required=False, widget=forms.Select(choices=UNIT, attrs={'class': 'search-components'}))
    profile = forms.CharField(label=_('profile'), required=False, widget=forms.Select(choices=PROFILE, attrs={'class': 'search-components'}))

    def clean_q(self):
        data = self.cleaned_data.get('q', '').split('}')
        if len(data) > 1:
            search_list = [re.split(r':.+\{', record) for record in data if record and len(re.split(r':.+\{', record)) == 2]
            search = []
            is_error = True
            for elastic_type, search_string in search_list:
                elastic_type = elastic_type.lower().strip()
                field, text = search_string.split(':')
                text = text.strip().replace('"', '').replace("'", '')
                if len(text.replace('*', '').replace('?', '')) > 2:
                    is_error = False
                search.append((elastic_type, {field: text}))
            if is_error:
                raise forms.ValidationError(_('Not enough characters for search'))
            return search
        elif len(data) == 1:
            if len(data[0].replace('*', '').replace('?', '')) < 2:
                raise forms.ValidationError(_('Not enough characters for search'))
            return [('_all', {'_all': data[0]})]
        raise forms.ValidationError(_('Not enough parameters for search'))
