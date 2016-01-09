from django.utils import formats
from django.core.urlresolvers import reverse

from rest_framework import serializers
# from rest_framework.reverse import reverse
from reversion import revisions as reversion

from measurements.models import Measurement


class RevisionsField(serializers.Field):
    """
    Returl list of revisions for object from django-revision
    """
    def __init__(self, **kwargs):
        super(RevisionsField, self).__init__(**kwargs)
        self.value = None

    def to_representation(self, obj):
        result = []
        for rev in list(reversion.get_for_object(obj)):
            result.append({
                'id': rev.revision.id,
                'url': reverse(
                    'measurements:api-revision',
                    kwargs={
                        'lab_pk': obj.unit.lab.pk,
                        'pk': obj.pk,
                        'revision_pk': rev.revision.id}
                ),
                'timestamp': formats.date_format(rev.revision.date_created, 'DATETIME_FORMAT'),
            })
        return result

    def get_attribute(self, obj):
        return obj


class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class MeasurementSerializer(serializers.ModelSerializer):

    headers = JSONSerializerField()
    table_data = JSONSerializerField()
    revisions = RevisionsField(required=False)

    class Meta:
        model = Measurement
        fields = ('headers', 'table_data', 'revisions')

    def update(self, instance, validated_data):
        """
        Update and return an existing `Measurement` instance, given the validated data.

        Doesn't hit DB if nothing changed(Doesn't create redundant revisions).
        """
        if instance.headers == validated_data.get('headers') and instance.table_data == validated_data.get('table_data'):
            return instance

        instance.headers = validated_data.get('headers', instance.headers)
        instance.table_data = validated_data.get('table_data', instance.table_data)
        instance.save()
        return instance