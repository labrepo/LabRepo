from django.conf import settings

from rest_framework import serializers
from reversion import revisions as reversion

from common.mixins import JsTreeMixin
from ..models import Unit, UnitLink


class RevisionCommentField(serializers.Field):
    """
    Serializes latest revision comment for object from django-revision
    """
    def __init__(self, **kwargs):
        super(RevisionCommentField, self).__init__(**kwargs)
        self.value = None

    def to_representation(self, obj):
        return obj

    def to_internal_value(self, data):
        self.value = data
        return data

    def get_attribute(self, obj):
        if self.value:
            return self.value
        elif list(reversion.get_for_object(obj)):
                return u'{}'.format(list(reversion.get_for_object(obj))[0].revision.comment)
        return ""


class UnitTableSerializer(serializers.ModelSerializer):
    """
    Serialises units to a handsontable table
    """

    readonly = serializers.SerializerMethodField('get_full_name')
    experiments_names = serializers.SerializerMethodField('get_experiments_titles')
    parents_names = serializers.SerializerMethodField('get_parents_titles')
    tags_names = serializers.SerializerMethodField('get_tags_titles')
    change_reasons = RevisionCommentField(required=False)

    def get_full_name(self, obj):
        return True

    def get_experiments_titles(self, obj):
        return obj.experiments.all().values_list('title')

    def get_parents_titles(self, obj):
        return obj.parent.all().values_list('sample')

    def get_tags_titles(self, obj):
        result = []
        for tag in obj.tags.all().values_list('details', 'color'):
            result.append({
                'text': tag[0],
                'color': tag[1] or '#ffffff'
            })
        return result

    def create(self, validated_data):
        if validated_data.get('change_reasons', None):
            del validated_data['change_reasons']

        return super(UnitTableSerializer, self).create(validated_data)

    class Meta:
        model = Unit
        fields = ('id', 'sample', 'experiments_names', 'parents_names', 'tags_names',  'readonly',
                  'change_reasons', 'experiments', 'parent', 'tags', 'lab')


class UnitSerializer(JsTreeMixin, serializers.ModelSerializer):
    """
    General Unit serializer
    """

    edit_permission = serializers.SerializerMethodField()
    tag_tree = serializers.SerializerMethodField()
    measurement = serializers.PrimaryKeyRelatedField(read_only=True)

    def get_edit_permission(self, obj):
        return obj.is_owner(self.context['request'].user)

    def get_tag_tree(self, obj):
        """
        Serialises unit tags to the jstree representation format
        """
        return self.get_jstree_data(obj.tags, fields=('id', 'parent', 'details'), parent_id='#')

    class Meta:
        model = Unit
        fields = ('id', 'sample', 'description', 'experiments', 'parent', 'tags', 'tag_tree', 'lab', 'measurement', 'edit_permission')


class UnitLinkSerializer(serializers.ModelSerializer):

    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = UnitLink
        fields = ('id', 'parent', 'link', 'timestamp', 'image', 'title', 'canonicalUrl',  'description')
