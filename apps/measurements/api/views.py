# -*- coding: utf-8 -*-
import json

from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from rest_framework import generics
from reversion import revisions as reversion

from common.mixins import LoginRequiredMixin, AjaxableResponseMixin, CheckLabPermissionMixin, RecentActivityMixin
from dashboard.models import RecentActivity
from measurements.api.serializers import MeasurementSerializer
from measurements.models import Measurement


class MeasurementDetailView(LoginRequiredMixin, CheckLabPermissionMixin, generics.RetrieveUpdateDestroyAPIView):

    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer

    def dispatch(self, *args, **kwargs):
        object = self.get_object()
        if not (object.unit.is_owner(self.request.user) or object.unit.is_member(self.request.user)):
            raise PermissionDenied
        return super(MeasurementDetailView, self).dispatch(*args, **kwargs)
