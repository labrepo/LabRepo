# -*- coding: utf-8 -*-
import json

from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Q

from rest_framework import generics

from common.mixins import LoginRequiredMixin, AjaxableResponseMixin, CheckLabPermissionMixin, RecentActivityMixin
from dashboard.models import RecentActivity
from units.api.serializers import UnitSerializer
from units.models import Unit
from experiments.models import Experiment
from labs.models import Lab


class UnitListView(LoginRequiredMixin, CheckLabPermissionMixin, generics.ListAPIView):

    serializer_class = UnitSerializer

    def get_queryset(self, **kwargs):
        if self.kwargs.get('experiment_pk'):
            experiments = [self.kwargs.get('experiment_pk')]
        else:
            experiments = Experiment.objects.filter(lab=self.lab, active=True)
            if self.lab.is_guest(self.request.user):
                experiments = experiments.filter(Q(owners=self.user) | Q(editors=self.user) | Q(viewers=self.user))
            experiments = experiments.values_list('id')
        return Unit.objects.filter(lab__pk=self.kwargs['lab_pk'], experiments__in=experiments, active=True)


class UnitUpdateView(LoginRequiredMixin, CheckLabPermissionMixin, RecentActivityMixin, AjaxableResponseMixin, View):

    serializer_class = UnitSerializer

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(UnitUpdateView, self).dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        results = []
        for index, unit_data in enumerate(json.loads(self.request.body)):
            if not unit_data:
                continue
            if 'lab' not in unit_data:
                unit_data['lab'] = self.lab.pk

            # check permission
            permission = False
            for experiment in Experiment.objects.filter(pk__in=unit_data['experiments']):
                if experiment.is_owner(self.request.user) or experiment.is_editor(self.request.user):
                    permission = True
                    break

            if not (self.lab.is_owner(self.request.user) or permission):
                results.append({'errors': {'non_field_error': 'Permission denied'}, 'success': False})
                continue

            try:
                if unit_data.get('pk', None):
                    unit = Unit.objects.get(pk=unit_data['pk'])
                    serializer = UnitSerializer(unit, data=unit_data)
                    self.flag = RecentActivity.UPDATE
                else:
                    raise Unit.DoesNotExist
            except Unit.DoesNotExist:
                serializer = UnitSerializer(data=unit_data)
                self.flag = RecentActivity.ADD

            if serializer.is_valid():
                unit = serializer.save()
                self.save_recent_activity(self.flag, obj=unit)
                results.append((index, {'pk': unit.pk, 'success': True}))
            else:
                results.append((index, {'errors': u'{}'.format(serializer.errors), 'success': False}))
        return self.render_to_json_response(results)

    def get_queryset(self, **kwargs):
        return Unit.objects.filter(lab__pk=self.kwargs['lab_pk'])