# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied

from rest_framework import generics
from reversion import revisions as reversion

from common.mixins import LoginRequiredMixin, CheckLabPermissionMixin, RecentActivityMixin
from dashboard.models import RecentActivity
from .serializers import MeasurementSerializer
from ..models import Measurement


class MeasurementDetailView(LoginRequiredMixin, RecentActivityMixin, CheckLabPermissionMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    View for handle unit's measurement.

    Note:
        A new measurement is created with a new unit creating
    """
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer

    def dispatch(self, *args, **kwargs):
        """Check user permissions"""
        object = self.get_object()

        if not object.unit.is_editor(self.request.user):
            raise PermissionDenied
        return super(MeasurementDetailView, self).dispatch(*args, **kwargs)

    def perform_update(self, serializer):
        """
        Update an existing `Measurement` instance, given the validated data.

        Doesn't hit DB if nothing changed(Doesn't create redundant revisions).
        """
        if not (self.get_object().headers == serializer.validated_data.get('headers') and
                self.get_object().table_data == serializer.validated_data.get('table_data')):
            with reversion.create_revision():
                serializer.save()
                reversion.set_user(self.request.user)
                self.save_recent_activity(RecentActivity.UPDATE, obj=self.get_object().unit, unit=self.get_object().unit.pk,
                                          experiment=[unicode(obj.pk) for obj in self.get_object().unit.experiments.all()])


class UnitRevisionView(LoginRequiredMixin, CheckLabPermissionMixin, generics.RetrieveAPIView):
    """Return a measurement instance by a revision id. Handle only GET requests."""

    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer
    object = None

    def get_object(self, *args, **kwargs):
        """Query a measurement by a revision pk"""
        if self.object:
            return self.object
        measurement = Measurement.objects.get(pk=kwargs['pk'])
        versions = reversion.get_for_object(measurement).filter(revision__pk=kwargs['revision_pk'])
        self.object = versions[0].object_version.object
        return self.object

    def dispatch(self, *args, **kwargs):
        """Check user permissions"""
        object = self.get_object(*args, **kwargs)
        if not object.unit.is_editor(self.request.user):
            raise PermissionDenied
        return super(UnitRevisionView, self).dispatch(*args, **kwargs)

