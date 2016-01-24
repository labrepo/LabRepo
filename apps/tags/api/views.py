# -*- coding: utf-8 -*-
from rest_framework import generics

from common.mixins import LoginRequiredMixin, CheckLabPermissionMixin
from tags.api.serializers import TagSerializer
from tags.models import Tag


class TagListView(LoginRequiredMixin, CheckLabPermissionMixin, generics.ListCreateAPIView):

    serializer_class = TagSerializer

    def get_queryset(self, **kwargs):
        return Tag.objects.filter(lab__pk=self.kwargs.get('lab_pk'))


class TagDetailView(LoginRequiredMixin, CheckLabPermissionMixin, generics.RetrieveUpdateDestroyAPIView):

    serializer_class = TagSerializer
    queryset = Tag.objects.all()

    def get_object(self):
        return Tag.objects.get(id=self.kwargs.get('pk'))
