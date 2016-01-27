from rest_framework import serializers

from ..models import Tag


class TagSerializer(serializers.ModelSerializer):
    """
    Serializes tags for the jstree library
    """
    text = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()

    def get_text(self, obj):
        return u'{}'.format(obj.details)

    def get_parent(self, obj):
        if obj.parent:
            return obj.parent.id
        return u'#'

    def get_icon(self, obj):
        return False

    class Meta:
        model = Tag
        fields = ('id', 'text', 'parent', 'icon')

