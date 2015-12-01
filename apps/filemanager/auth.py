from labs.models import Lab


def allow_all(request, **kwargs):
    return True


def require_staff(request, **kwargs):
    return request.user.is_staff


def require_superuser(request, **kwargs):
    return request.user.is_superuser


def allow_in_lab(self, **kwargs):
    lab = Lab.objects.get(pk=kwargs.get('lab_pk'))
    if not 'lab' in self.request.session:
        self.request.session['lab'] = unicode(lab.id)
    return lab.is_assistant(self.request.user)

