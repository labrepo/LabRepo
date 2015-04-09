from django.conf import settings
from django.utils.module_loading import import_by_path
from django.http import HttpResponseForbidden
from functools import wraps


auth_callback = getattr(settings, 'FILEMANAGER_AUTH_CALLBACK', 'filemanager.auth.allow_all')

if isinstance(auth_callback, basestring):
    auth_callback = import_by_path(auth_callback)


def filemanager_require_auth(fn):
    @wraps(fn)
    def view(request, *args, **kwargs):
        if auth_callback(request, **kwargs):
            return fn(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()
    return view
