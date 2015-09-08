import json
from itertools import groupby
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from mongoengine import Q

from common.mixins import ActiveTabMixin, LoginRequiredMixin, AjaxableResponseMixin
from dashboard.documents import RecentActivity
from experiments.documents import Experiment
from labs.documents import Lab


class DashboardView(ActiveTabMixin, LoginRequiredMixin, ListView):
    model = RecentActivity
    context_object_name = 'recent'
    template_name = 'dashboard/dashboard.html'
    active_tab = 'dashboard'
    paginate_by = 10

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        user = [self.request.user]
        if not Lab.objects.filter(Q(investigator__in=user) | Q(members__in=user) | Q(guests__in=user)):
            raise PermissionDenied
        return super(DashboardView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(DashboardView, self).get_context_data(**kwargs)
        ctx['experiments'] = self.get_experiments()
        return ctx

    def get_experiments(self):
        experiments = []
        for experiment in Experiment.objects.filter(lab=self.kwargs['lab_pk'], active=True):
            experiments.append({
                'url': reverse('experiments:detail', kwargs={'lab_pk': self.kwargs.get('lab_pk'), 'pk': experiment.pk}),
                'edit_url': reverse('experiments:update-date',
                                    kwargs={'lab_pk': self.kwargs.get('lab_pk'), 'pk': experiment.pk}),
                'title': experiment.title,
                'start': experiment.start.isoformat(),
                'end': experiment.end.isoformat(),
                'backgroundColor': "#5cb85c",
                'borderColor': "#5cb85c",
                'allDay': False,
                'editable': experiment.is_member(self.request.user) or experiment.is_owner(self.request.user)
            })
        return json.dumps(experiments)


class RecentActivityView(LoginRequiredMixin, AjaxableResponseMixin, ListView):
    model = RecentActivity
    template_name = 'dashboard/tab_recent_activity.html'
    paginate_by = 1

    def get_queryset(self):
        queryset = self.model.objects.filter(lab_id=self.kwargs.get('lab_pk'))
        if self.kwargs.get('experiment_pk'):
            queryset = queryset.filter(extra__experiment=self.kwargs.get('experiment_pk'))
        return group_by_date(queryset.select_related(max_depth=2))

    def get_context_data(self, **kwargs):
        ctx = super(RecentActivityView, self).get_context_data(**kwargs)
        if self.kwargs.get('experiment_pk'):
            ctx['pagination_url'] = reverse('dashboard:experiment-all-activity',
                                            kwargs={'lab_pk': self.kwargs.get('lab_pk'),
                                                    'experiment_pk': self.kwargs.get('experiment_pk')})
        else:
            ctx['pagination_url'] = reverse('dashboard:all-activity', kwargs={'lab_pk': self.kwargs.get('lab_pk')})
        return ctx


class MeasurementRecentActivityView(LoginRequiredMixin, AjaxableResponseMixin, ListView):
    model = RecentActivity
    template_name = 'dashboard/tab_recent_activity.html'
    paginate_by = 1

    def get_queryset(self):
        queryset = self.model.objects.filter(lab_id=self.kwargs.get('lab_pk'), instance_type='Measurement')
        if self.kwargs.get('experiment_pk'):
            queryset = queryset.filter(extra__experiment=self.kwargs.get('experiment_pk'))
        return group_by_date(queryset.select_related(max_depth=2))

    def get_context_data(self, **kwargs):
        ctx = super(MeasurementRecentActivityView, self).get_context_data(**kwargs)
        if self.kwargs.get('experiment_pk'):
            ctx['pagination_url'] = reverse('dashboard:experiment-measurement-activity',
                                            kwargs={'lab_pk': self.kwargs.get('lab_pk'),
                                                    'experiment_pk': self.kwargs.get('experiment_pk')})
        else:
            ctx['pagination_url'] = reverse('dashboard:measurement-activity',
                                            kwargs={'lab_pk': self.kwargs.get('lab_pk')})
        return ctx


class CommentRecentActivityView(LoginRequiredMixin, AjaxableResponseMixin, ListView):
    model = RecentActivity
    template_name = 'dashboard/tab_recent_activity.html'
    paginate_by = 1

    def get_queryset(self):
        queryset = self.model.objects.filter(lab_id=self.kwargs.get('lab_pk'), instance_type='Comment')
        if self.kwargs.get('experiment_pk'):
            queryset = queryset.filter(extra__experiment=unicode(self.kwargs.get('experiment_pk')))
        return group_by_date(queryset.select_related(max_depth=2))

    def get_context_data(self, **kwargs):
        ctx = super(CommentRecentActivityView, self).get_context_data(**kwargs)
        if self.kwargs.get('experiment_pk'):
            ctx['pagination_url'] = reverse('dashboard:experiment-comment-activity',
                                            kwargs={'lab_pk': self.kwargs.get('lab_pk'),
                                                    'experiment_pk': self.kwargs.get('experiment_pk')})
        else:
            ctx['pagination_url'] = reverse('dashboard:comment-activity', kwargs={'lab_pk': self.kwargs.get('lab_pk')})
        return ctx


def group_by_date(queryset):
    return sorted([(k, tuple(v))
                   for k, v in groupby(queryset, key=lambda x: x.action_time.date())],
                  reverse=True)