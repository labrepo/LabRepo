import os.path

from filemanager import fields
from django.db.models import FileField

from django.conf import settings

MEDIA_ROOT = settings.MEDIA_ROOT
UPLOAD_ROOT = getattr(settings, 'FILEMANAGER_UPLOAD_ROOT', MEDIA_ROOT)

if not UPLOAD_ROOT.startswith(MEDIA_ROOT):
    raise ValueError("FILEMANAGER_UPLOAD_ROOT must be below MEDIA_ROOT")

UPLOAD_DIFFERENCE = UPLOAD_ROOT[len(MEDIA_ROOT)]


class FileBrowserField(FileField):
    def __init__(self, *args, **kwargs):
        defaults = {
            'upload_to': '',
        }
        defaults.update(kwargs)
        defaults['upload_to'] = os.path.join(
            UPLOAD_DIFFERENCE, defaults['upload_to'])
        super(FileBrowserField, self).__init__(*args, **defaults)

    def formfield(self, **kwargs):
        if self.null:
            form_class = fields.ClearableFileBrowserField
        else:
            form_class = fields.FileBrowserField

        defaults = {
            'form_class': form_class,
        }
        defaults.update(kwargs)

        return super(FileBrowserField, self).formfield(**defaults)

    def pre_save(self, model_instance, add):
        # Skip the pre_save of the FileField, as that tries to save the file
        # again, resulting in duplicates
        f = super(FileField, self).pre_save(model_instance, add)
        return f


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^filemanager\.models\.FileBrowserField"])
except ImportError:
    pass
