from rest_framework import serializers
from units.models import Unit
from reversion import revisions as reversion


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
        else:
            return u'{}'.format(list(reversion.get_for_object(obj))[0].revision.comment)


class UnitSerializer(serializers.ModelSerializer):

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
        return obj.tags.all().values_list('details')

    class Meta:
        model = Unit
        fields = ('id', 'sample', 'experiments_names', 'parents_names', 'tags_names',  'readonly', 'change_reasons', 'experiments', 'parent', 'tags', 'lab' )