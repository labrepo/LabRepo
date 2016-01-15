from django.db.models import Q
from django.conf import settings

from experiments.models import Experiment
from labs.models import Lab


def menu_processor(request):
    """Return experiment and lab instances which is available for current user."""
    if request.resolver_match and 'lab_pk' in request.resolver_match.kwargs:
        lab_pk = request.resolver_match.kwargs['lab_pk']
        user = request.user
        lab = Lab.objects.get(pk=lab_pk)
        if not unicode(lab.id) == request.session.get('lab'):
            request.session['lab'] = unicode(lab.id)
        experiments = Experiment.objects.filter(lab=lab_pk, active=True)
        if lab.is_guest(user):
            experiments = experiments.filter(Q(owners=user) | Q(editors=user) | Q(viewers=user))
        return {'experiments_list': experiments,
                'lab': lab,
                'labs_list': Lab.objects.filter((Q(investigator=user) | Q(members=user) | Q(guests=user))).exclude(pk__in=[lab_pk])
                }
    return {}


def sidebar_processor(request):
    """
    Save state of a sidebar, collapsed or not.
    """
    if request.COOKIES.get('sidebarcollapse'):
        return {'SIDEBAR_COLLAPSED': True}
    return {}


def js_variables_processor(request):
    """
    Add variables which are used in js code
    """
    return {
        'DOMAIN': settings.DOMAIN,
        'DEBUG': settings.DEBUG,
    }
