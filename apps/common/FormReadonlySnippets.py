from django import forms
from django.utils.safestring import mark_safe


class ReadonlyWidget(forms.Widget):
    """Renders a value wrapped in a <p class='form-control-static'> tag.
    
    Requires use of specific form support. (see ReadonlyForm 
    or ReadonlyModelForm)
    """

    def render(self, name, value, attrs=None):
        return mark_safe(u'<p %s >%s</p>' % (forms.util.flatatt({'class': 'form-control-static'}), value))

    def value_from_datadict(self, data, files, name):
        return self.original_value


class PField(forms.Field):
    """A field which renders a value wrapped in a <p> tag.
    
    Requires use of specific form support. (see ReadonlyForm 
    or ReadonlyModelForm)
    """
    
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = kwargs.get('widget', ReadonlyWidget)
        super(PField, self).__init__(*args, **kwargs)


class Readonly(object):
    """Base class for ReadonlyForm and ReadonlyModelForm which provides
    the meat of the features described in the docstings for those classes.
    """

    def __init__(self, *args, **kwargs):
        super(Readonly, self).__init__(*args, **kwargs)
        from django.forms.widgets import Select
        readonly = self.NewMeta.readonly_fields
        if not readonly:
            return
        for name, field in self.fields.items():
            if name in readonly:
                if isinstance(field.widget, Select):
                    field.widget.attrs['disabled'] = True
                else:
                    field.widget = ReadonlyWidget(attrs={'class': 'form-control-static'})
            elif not isinstance(field, PField):
                continue

    class NewMeta:
        readonly_fields = tuple()