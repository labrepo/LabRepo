# -*- coding: utf-8 -*-
import dateutil
import json
import requests
import re
import logging

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _, ugettext
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, View
from django.views.generic.edit import ModelFormMixin, ProcessFormView

from comments.models import Comment
from common.decorators import get_obj_or_404
from common.mixins import (ActiveTabMixin, CheckEditPermissionMixin, CheckViewPermissionMixin,
                           LabQueryMixin, CheckDeletePermissionMixin, RecentActivityMixin,
                           AjaxableResponseMixin, InviteFormMixin, CheckLabPermissionMixin,
                           FormInitialMixin, LoginRequiredMixin)
from dashboard.models import RecentActivity
from tags.models import Tag
from units.models import Unit
from filemanager.views import get_upload
from .models import Experiment, ExperimentReadCommentEntry
from .forms import ExperimentForm, ExperimentUpdateForm, UpdateUnitsForm


logger = logging.getLogger(__name__)
class ExperimentCreateView(CheckLabPermissionMixin, LabQueryMixin, FormInitialMixin, InviteFormMixin, ActiveTabMixin,
                           RecentActivityMixin, CreateView):
    """
     View for creating a new experiment
    """
    model = Experiment
    form_class = ExperimentForm
    template_name = 'experiments/experiment_form.html'
    active_tab = 'experiments'

    def form_valid(self, form):
        """
        If form is valid save create a new experiment, if created user not in owners, add him there

        :param form: :class:`experiments.forms.ExperimentForm` instance
        :return: redirect to detail laboratory's information
        """
        self.object = form.save(commit=False)
        self.object.lab = self.lab
        self.object.save()
        if not self.request.user in self.object.owners.all():
            self.object.owners.add(self.request.user)
        if not set(self.lab.investigator.all()) & set(self.object.owners.all()):
            a = set(self.lab.investigator.all()) - set(self.object.owners.all())
            a = list(a)
            self.object.owners.add(*a)

        try:
            self.object.wooflo_key = get_wooflo_key(self.object)
        except Exception as e:
            logger.exception("Fatal error while a wooflo key generation")

        self.object.save()
        self.save_recent_activity(RecentActivity.ADD)
        self.get_success_message()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return self.lab.get_absolute_url()

    def get_success_message(self):
        return messages.add_message(self.request, messages.SUCCESS, _('Experiment was added successfully.'))


class ExperimentUpdateView(CheckLabPermissionMixin, InviteFormMixin, CheckEditPermissionMixin, LabQueryMixin,
                           RecentActivityMixin, UpdateView):
    """
    View for updating an existing experiment
    """
    model = Experiment
    form_class = ExperimentForm
    template_name = 'experiments/experiment_form.html'

    def form_valid(self, form):
        """
        If form is valid save update an experiment, if updated user not in owners, add him there

        :param form: :class:`experiments.forms.ExperimentForm` instance
        :return: redirect to detail laboratory's information
        """
        lab = self.object.lab
        self.object = form.save(commit=False)
        if not set(lab.investigator.all()) & set(self.object.owners.all()):
            self.object.owners.add(list(set(lab.investigator) - set(self.object.owners)))
        self.object.lab = lab
        self.object.save()
        self.save_recent_activity(RecentActivity.UPDATE, experiment=self.object)
        self.get_success_message()
        return HttpResponseRedirect(self.get_success_url())

    @method_decorator(get_obj_or_404)
    def get_initial(self):
        self.initial = {'lab': self.object.lab, 'user': self.request.user}
        return super(ExperimentUpdateView, self).get_initial()

    def get_success_url(self):
        return reverse('experiments:detail', kwargs={'pk': self.object.pk, 'lab_pk': self.object.lab.pk})

    def get_success_message(self):
        return messages.add_message(self.request, messages.SUCCESS, _('Experiment was updated successfully.'))


class ExperimentUpdateDateView(CheckLabPermissionMixin, CheckEditPermissionMixin, LabQueryMixin,
                               RecentActivityMixin, AjaxableResponseMixin, UpdateView):
    """
    View for updating date an existing experiment
    """
    model = Experiment
    form_class = ExperimentUpdateForm
    template_name = 'dashboard/resent.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        data = self.request.POST
        self.object.start = dateutil.parser.parse(data['start'])
        self.object.end = dateutil.parser.parse(data['end'])
        self.object.save()
        resent = self.save_recent_activity(RecentActivity.UPDATE)
        return self.render_to_json_response({'data': render_to_string(self.template_name, {'object': resent})})


class ExperimentDeleteView(CheckLabPermissionMixin, CheckDeletePermissionMixin, LabQueryMixin, ActiveTabMixin,
                           RecentActivityMixin, DeleteView):
    """
    View for removing an existing experiment
    """
    model = Experiment
    active_tab = 'experiments'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.active = False
        self.object.save()
        self.save_recent_activity(RecentActivity.DELETE)
        self.get_success_message()
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return reverse_lazy('labs:detail', kwargs={'lab_pk': self.kwargs.get('lab_pk')})

    def get_success_message(self):
        return messages.add_message(self.request, messages.SUCCESS, _('Experiment was removed successfully.'))


class ExperimentDetailView(CheckLabPermissionMixin, CheckViewPermissionMixin, LabQueryMixin, DetailView):
    """
    View for display information about an existing experiment with related units
    """
    model = Experiment
    template_name = 'experiments/experiment_detail.html'
    paginate_by = 5

    def get_unit_graph_data(self):
        """
        Return json data for units graph
        """
        units = list(self.units)
        graph_data = dict()

        graph_data['graph'] = []
        graph_data['directed'] = False
        graph_data['multigraph'] = False

        nodes = []
        links = []

        for index, unit in enumerate(units):
            node = {
                "size": 1,
                "score": 2,
                "id": u'{}'.format(unit.pk),
                "text": u'{}'.format(unit.sample),
                "type": "circle",
                'link': unit.get_absolute_url(),
            }
            nodes.append(node)
            if not unit.parent:
                continue
            for parent in unit.parent.all():
                if parent in units:
                    link = {
                        'target': index,
                        'source': units.index(parent),
                        'arrow': True
                    }
                    links.append(link)

        graph_data['nodes'] = nodes
        graph_data['links'] = links

        return mark_safe(json.dumps(graph_data))

    def get_context_data(self, *args, **kwargs):
        try:
            if not self.object.wooflo_key:
                self.object.wooflo_key = get_wooflo_key(self.object)
                self.object.save()
        except Exception as e:
            logger.exception("Fatal error while a wooflo key generation")

        ctx = super(ExperimentDetailView, self).get_context_data(**kwargs)
        self.units = Unit.objects.filter(experiments=self.object, active=True)
        ctx['units'] = self.units
        ctx['units_graph_json'] = self.get_unit_graph_data()

        # ctx['unit_form'] = AddUnitToExperimentForm(initial={'lab': self.lab, 'user': self.request.user, 'experiment': self.object})

        UPLOAD_URL, UPLOAD_ROOT = get_upload(self.request, lab_pk=self.lab.pk, *args, **kwargs)
        ctx['UPLOAD_URL'] = UPLOAD_URL
        return ctx


class ExperimentAddUnits(LoginRequiredMixin, CheckLabPermissionMixin, FormInitialMixin, AjaxableResponseMixin,
                          RecentActivityMixin, ModelFormMixin, ProcessFormView, View):
    """
    Add units to a experiment
    """
    model = Experiment
    form_class = UpdateUnitsForm

    def post(self, request, *args, **kwargs):
        self.object = None
        return super(ExperimentAddUnits, self).post(request, *args, **kwargs)

    def form_valid(self, form):

        self.object = form.cleaned_data['experiment']

        if not (self.object.is_owner(self.request.user) or self.object.is_member(self.request.user)):
            raise PermissionDenied

        for unit in form.cleaned_data['units']:
            unit.experiments.add(self.object)
            unit.user = self.request.user
            unit.save()

        self.save_recent_activity(RecentActivity.UPDATE)
        self.get_success_message()
        return self.render_to_json_response({'message': self.get_success_message()})

    def get_success_message(self):
        return ugettext(u'Experiment was changed successfully.')

def get_wooflo_key(experiment):  # TODO: Refactor this
    """
    Interacts with a wooflo server and create new wooflo project.
    """
    s = requests.Session()
    r = s.get('http://wooflo.magic60.ru/signin', timeout=3)
    rr = re.search(r'<input id="csrf_token" name="csrf_token" type="hidden" value="(.*?)">', r.text)
    token = rr.group(1)
    r = s.post('http://wooflo.magic60.ru/signin', data={
        'LoginEmail': 'cyc60@mail.ru',
        'LoginPassword': '1',
        'csrf_token': token,
    })
    headers = {
        'X-CSRFToken': token,
    }
    payload = {
        'Name': u'{}'.format(experiment.title),
        'PublicView': True,
        'PublicEdit': True,
        'csrf_token': token,
    }

    r = s.post('http://wooflo.magic60.ru/projects', files={'value_1': (None, '12345')}, headers=headers, data=payload)
    return r.json()['pk']


class ExperimentReadComment(LoginRequiredMixin, CheckLabPermissionMixin, AjaxableResponseMixin, View):
    """
    Update last read comment for this experiment for current user
    """
    def post(self, *args, **kwargs):
        comment_id = self.request.POST.get('comment')
        experiment = Experiment.objects.get(id=kwargs.get('pk'))

        entry = ExperimentReadCommentEntry.objects.update_or_create(
            user=self.request.user,
            experiment=experiment,
            defaults={
                'comment': Comment.objects.get(pk=comment_id)
            })
        return self.render_to_json_response({'message': 'ok'})
