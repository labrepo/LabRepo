from mongoengine import Q

from experiments.documents import Experiment
from labs.documents import Lab


def menu_processor(request):
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
                'labs_list': Lab.objects.filter((Q(investigator=user) | Q(members=user) | Q(guests=user)),
                                                pk__not__in=[lab_pk])
                }
    return {}
