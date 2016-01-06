from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

from profiles.api.serializers import LabUserSerializer
from comments.models import Comment
from units.models import Unit
from experiments.models import Experiment


class InstanceTypeField(serializers.Field):
    """
    Serialize django content type field from a generic relation.
    """

    def to_representation(self, obj):
        return obj.name.lower()

    def to_internal_value(self, obj):
        if obj.lower() == 'experiment':
            model = Experiment
        if obj.lower() == 'unit':
            model = Unit
        content_type = ContentType.objects.get_for_model(model)
        return content_type


class CommentSerializer(serializers.ModelSerializer):

    instance_type = InstanceTypeField()
    init_user_info = LabUserSerializer(source='init_user', required=False, read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'init_user', 'init_user_info', 'instance_type', 'object_id',  'action_time', 'text')