from labs.documents import Lab


def allow_all(request, **kwargs):
    return True


def require_staff(request, **kwargs):
    return request.user.is_staff


def require_superuser(request, **kwargs):
    return request.user.is_superuser


def allow_in_lab(request, **kwargs):
    lab = Lab.objects.get(pk=kwargs.get('lab_pk'))
    if not 'lab' in request.session:
        request.session['lab'] = unicode(lab.id)
    return lab.is_assistant(request.user)

