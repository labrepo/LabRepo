from rest_framework import serializers

from profiles.api.serializers import LabUserSerializer
from ..models import RecentActivity


class InstanceTypeField(serializers.Field):
    """Serialize django content type field from a generic relation to string."""

    def to_representation(self, obj):
        return obj.name.lower()


class ContentObjectField(serializers.Field):
    """Serialize content object from a generic relation to string"""

    def to_representation(self, obj):
        return unicode(obj)


class ContentObjectLinkField(serializers.Field):
    """Serialize content object from a generic relation to a url"""

    def to_representation(self, obj):
        return obj.get_absolute_url()


class RecentActivitySerializer(serializers.ModelSerializer):

    content_type = InstanceTypeField(read_only=True)
    content_object = ContentObjectField(read_only=True)
    content_object_link = ContentObjectLinkField(read_only=True)
    init_user_info = LabUserSerializer(source='init_user', required=False, read_only=True)
    action_flag = serializers.SerializerMethodField()

    def get_action_flag(self, obj):
        return u'{}'.format(obj.get_action_flag_display())

    class Meta:
        model = RecentActivity
        fields = ('id', 'experiments', 'value', 'init_user_info',  'content_type', 'object_id',
                  'content_object', 'content_object_link','action_flag', 'action_time')