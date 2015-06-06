# -*- coding: utf-8 -*-
import dateutil

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView

from comments.documents import Comment
from common.decorators import get_obj_or_404
from common.mixins import (ActiveTabMixin, CheckEditPermissionMixin, CheckViewPermissionMixin,
                           LabQueryMixin, CheckDeletePermissionMixin, RecentActivityMixin, CommentMixin,
                           AjaxableResponseMixin, InviteFormMixin, CheckLabPermissionMixin, FormInitialMixin)
from dashboard.documents import RecentActivity
from experiments.documents import Experiment
from experiments.forms import ExperimentForm, ExperimentUpdateForm
from units.documents import Unit


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
        if not self.request.user in self.object.owners:
            self.object.owners.append(self.request.user)
        self.object.lab = self.lab
        if not set(self.lab.investigator) & set(self.object.owners):
            self.object.owners.extend(list(set(self.lab.investigator) - set(self.object.owners)))
        self.object.save()
        self.save_recent_activity(RecentActivity.ADD, experiment=unicode(self.object.pk))
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
        if not set(lab.investigator) & set(self.object.owners):
            self.object.owners.extend(list(set(lab.investigator) - set(self.object.owners)))
        self.object.lab = lab
        self.object.save()
        self.save_recent_activity(RecentActivity.UPDATE, experiment=unicode(self.object.pk))
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
        resent = self.save_recent_activity(RecentActivity.UPDATE, experiment=unicode(self.object.pk))
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
        self.save_recent_activity(RecentActivity.DELETE, **{self.model._meta.object_name.lower(): self.object.pk})
        self.get_success_message()
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return reverse_lazy('labs:detail', kwargs={'lab_pk': self.kwargs.get('lab_pk')})

    def get_success_message(self):
        return messages.add_message(self.request, messages.SUCCESS, _('Experiment was removed successfully.'))


class ExperimentDetailView(CheckLabPermissionMixin, CheckViewPermissionMixin, LabQueryMixin, CommentMixin, DetailView):
    """
    View for display information about an existing experiment with related units
    """
    model = Experiment
    template_name = 'experiments/experiment_detail.html'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        ctx = super(ExperimentDetailView, self).get_context_data(**kwargs)
        ctx['units'] = self.units
        ctx['tags'] = set([tag for unit in self.units for tag in unit.tags])
        # ctx['measurements'] = [measurement for unit in self.units for measurement in unit.measurements if measurement.active]
        ctx['measurements'] = [unit.measurements  for unit in self.units]
                              # self.units.filter(measurements__match={"active": True})
        return ctx

    def get_list_comment(self):
        self.units = Unit.objects.filter(experiments=self.object, active=True)
        queryset = list(super(ExperimentDetailView, self).get_list_comment())
        queryset += list(Comment.objects.filter(instance_type='Unit', object_id__in=self.units.values_list('pk')))
        return queryset
