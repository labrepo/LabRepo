# -*- coding: utf-8 -*-
from ckeditor.widgets import CKEditorWidget
from django.core.urlresolvers import reverse
from django.forms import DateTimeInput
from django.utils.safestring import mark_safe


class DateTimeWidget(DateTimeInput):
    class Media:
        css = {
            'all': ('datetimepicker/css/bootstrap-datetimepicker.min.css',)
        }
        js = ('bootstrap/js/bootstrap.min.js', 'datetimepicker/js/moment.js',
              'datetimepicker/js/bootstrap-datetimepicker.min.js', 'js/datetimepicker.js')

    def render(self, name, value, attrs=None):
        attrs['data-date-format'] = "MM/DD/YYYY HH:mm"
        html = super(DateTimeWidget, self).render(name, value, attrs)
        return mark_safe('<div class="datetimepicker-container input-group date">' + html +
                         '<span class="input-group-addon">' +
                         '<span class="glyphicon glyphicon-calendar"></span></span></div>')


class CKEditorUploadWidget(CKEditorWidget):
    def __init__(self, config_name='default', extra_plugins=None, external_plugin_resources=None, *args, **kwargs):
        url = reverse('filemanager-include', kwargs={'lab_pk': kwargs.pop('lab_pk')})
        super(CKEditorUploadWidget, self).__init__(config_name, extra_plugins, external_plugin_resources, *args,
                                                   **kwargs)
        self.config['filebrowserUploadUrl'] = self.config['filebrowserBrowseUrl'] = url
