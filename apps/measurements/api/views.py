# -*- coding: utf-8 -*-
import json

from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from rest_framework.views import APIView
from rest_framework import generics
from reversion import revisions as reversion

from common.mixins import LoginRequiredMixin, AjaxableResponseMixin, CheckLabPermissionMixin, RecentActivityMixin
from dashboard.models import RecentActivity
from measurements.api.serializers import MeasurementSerializer
from measurements.models import Measurement



class MeasurementDetailView(LoginRequiredMixin, CheckLabPermissionMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    View for handle unit's measurement.

    Note:
        A new measurement is created with a new unit creating

    """
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer

    def dispatch(self, *args, **kwargs):
        """
        Check user permissions
        """
        object = self.get_object()

        if not (object.unit.is_owner(self.request.user) or object.unit.is_member(self.request.user)):
            raise PermissionDenied
        return super(MeasurementDetailView, self).dispatch(*args, **kwargs)

    def perform_update(self, serializer):
        with reversion.create_revision():
            serializer.save()
            reversion.set_user(self.request.user)


class UnitRevisionView(LoginRequiredMixin, CheckLabPermissionMixin, generics.RetrieveAPIView):

    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer
    object = None

    def get_object(self, *args, **kwargs):
        """
        """
        if self.object:
            return self.object
        measurement = Measurement.objects.get(pk=kwargs['pk'])
        versions = reversion.get_for_object(measurement).filter(revision__pk=kwargs['revision_pk'])
        self.object = versions[0].object_version.object
        return self.object

    def dispatch(self, *args, **kwargs):
        object = self.get_object(*args, **kwargs)
        if not (object.unit.is_owner(self.request.user) or object.unit.is_member(self.request.user)):
            raise PermissionDenied
        return super(UnitRevisionView, self).dispatch(*args, **kwargs)

