import os

from rest_framework import serializers

from storages.models import LabStorage


class LabStorageSerializer(serializers.ModelSerializer):

    fullname = serializers.SerializerMethodField()
    # password = serializers.ReadOnlyField()
    file_info = serializers.SerializerMethodField()

    def get_fullname(self, obj):
        return u'{}'.format(obj)

    def get_file_info(self, obj):
        if obj.key_file:
            return {
                'name': os.path.basename(obj.key_file.name)
            }
        return ''

    class Meta:
        model = LabStorage
        fields = ('id', 'lab', 'type', 'readonly', 'username', 'host', 'path',
                  'folder_name', 'password', 'port',  'key_file', 'fullname', 'file_info')
        extra_kwargs = {'password': {'write_only': True}}
