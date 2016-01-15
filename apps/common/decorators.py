from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404


def get_obj_or_404(view_func):
    """Handle ObjectDoesNotExist exception"""
    @wraps(view_func)
    def wrapped_view_func(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except ObjectDoesNotExist:
            raise Http404
    return wrapped_view_func

