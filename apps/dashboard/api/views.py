# -*- coding: utf-8 -*-
from django.db.models import Q

from rest_framework import generics
from rest_framework import filters

from common.mixins import LoginRequiredMixin, CheckLabPermissionMixin
from .serializers import RecentActivitySerializer
from ..models import RecentActivity


class RecentActivityListView(LoginRequiredMixin, CheckLabPermissionMixin, generics.ListAPIView):

    serializer_class = RecentActivitySerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = {'action_time': ['lt', 'gt']}

    def get_queryset(self, **kwargs):
        queryset = RecentActivity.objects.filter(lab_id=self.lab)
        if self.kwargs.get('experiment_pk'):
            queryset = queryset.filter(experiments__pk=self.kwargs.get('experiment_pk'))
        return queryset


class MeasurementActivityListView(LoginRequiredMixin, CheckLabPermissionMixin, generics.ListAPIView):

    serializer_class = RecentActivitySerializer

    def get_queryset(self):
        queryset = RecentActivity.objects.filter(lab_id=self.kwargs.get('lab_pk'), content_type__model='measurement')

        if self.kwargs.get('experiment_pk'):
            queryset = queryset.filter(experiments__pk=self.kwargs.get('experiment_pk'))
        return queryset.select_related()


class CommentActivityListView(LoginRequiredMixin, CheckLabPermissionMixin, generics.ListAPIView):

    serializer_class = RecentActivitySerializer

    def get_queryset(self):
        queryset = RecentActivity.objects.filter(lab_id=self.kwargs.get('lab_pk')).filter(Q(content_type__model='comment') | Q(action_flag=RecentActivity.COMMENT))
        if self.kwargs.get('experiment_pk'):
            queryset = queryset.filter(experiments__pk=unicode(self.kwargs.get('experiment_pk')))
        return queryset.select_related()

