from rest_framework import serializers
from units.models import Unit


class UnitSerializer(serializers.ModelSerializer):

    readonly = serializers.SerializerMethodField('get_full_name')
    experiments_names = serializers.SerializerMethodField('get_experiments_titles')
    parents_names = serializers.SerializerMethodField('get_parents_titles')
    tags_names = serializers.SerializerMethodField('get_tags_titles')

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
        fields = ('id', 'sample', 'experiments_names', 'parents_names', 'tags_names',  'readonly', 'description', 'experiments', 'parent', 'tags', 'lab' )