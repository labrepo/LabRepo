from rest_framework import serializers
from measurements.models import Measurement


class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class MeasurementSerializer(serializers.ModelSerializer):

    headers = JSONSerializerField()
    table_data = JSONSerializerField()

    class Meta:
        model = Measurement
        fields = ('headers', 'table_data')