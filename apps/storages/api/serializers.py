import os

from rest_framework import serializers

from storages.models import LabStorage


class LabStorageSerializer(serializers.ModelSerializer):

    fullname = serializers.SerializerMethodField()
    key_file = serializers.FileField(required=False, max_length=None, allow_empty_file=True)

    def get_fullname(self, obj):
        return u'{}'.format(obj)

    class Meta:
        model = LabStorage
        fields = ('id', 'lab', 'type', 'readonly', 'username', 'host', 'path',
                  'folder_name', 'password', 'port',  'key_file', 'fullname', 'key_file_name')
        extra_kwargs = {'password': {'write_only': True}}
