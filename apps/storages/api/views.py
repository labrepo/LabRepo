# -*- coding: utf-8 -*-
import base64
from django.core.files.base import ContentFile

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from common.mixins import LoginRequiredMixin, CheckLabPermissionMixin
from .serializers import LabStorageSerializer
from ..models import LabStorage


class StorageListView(LoginRequiredMixin, CheckLabPermissionMixin, generics.ListCreateAPIView):

    serializer_class = LabStorageSerializer

    def get_queryset(self, **kwargs):
        return LabStorage.objects.filter(lab__pk=self.kwargs.get('lab_pk'))

    def create(self, request, *args, **kwargs):
        """
        Save ssh key file content.

        Save ssh key file content to the db(a "public_key" field).
        Save a filename to a "key_file_name" field.
        The file itself isn't saved.
        """

        key_file = request.data.get('key_file', None)
        if key_file:
            del request.data['key_file']

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        if key_file:
            tmp_file = key_file['data'].partition('base64,')[2]
            obj.public_key = base64.b64decode(tmp_file)
            obj.key_file_name = key_file['name']
            obj.save()

        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class StorageDetailView(LoginRequiredMixin, CheckLabPermissionMixin, generics.RetrieveUpdateDestroyAPIView):

    serializer_class = LabStorageSerializer
    queryset = LabStorage.objects.all()

    def get_object(self):
        return LabStorage.objects.get(id=self.kwargs.get('pk'))

    def update(self, request, *args, **kwargs):
        """
        Save ssh key file content.

        Save ssh key file content to the db(a "public_key" field).
        Save a filename to a "key_file_name" field.
        The file itself isn't saved.
        """
        key_file = request.data.get('key_file', None)
        if key_file:
            del request.data['key_file']

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        if key_file:
            tmp_file = key_file['data'].partition('base64,')[2]
            obj.public_key = base64.b64decode(tmp_file)
            obj.key_file_name = key_file['name']
            obj.save()

        return Response(serializer.data)
