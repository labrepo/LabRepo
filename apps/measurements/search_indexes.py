from elasticutils.contrib.django import MappingType, Indexable

from units.models import Unit


class MeasurementMappingType(MappingType, Indexable):
    @classmethod
    def get_model(cls):
        """Returns the Django model this MappingType relates to measurements"""
        return Unit

    @classmethod
    def get_mapping_type_name(cls):
        """Returns the name of the mapping.

        By default, this is::

            cls.get_model()._meta.db_table

        Override this if you want to compute the mapping type name
        differently.

        :returns: mapping type string

        """
        return 'measurements_measurement'

    @classmethod
    def extract_document(cls, obj_id, obj=None):
        """Extracts the Elasticsearch index document for this instance

        .. Note::

           The resulting dict must be JSON serializable.

        :arg obj_id: the object id for the object to extract from
        :arg obj: if this is not None, use this as the object to
            extract from; this allows you to fetch a bunch of items
            at once and extract them one at a time

        :returns: dict of key/value pairs representing the document

        """
        if obj is None:
            obj = cls.get_model().get(id=obj_id)
        doc = [{
            '_parent': unicode(obj.pk),
            'id': unicode(measurement.id),
            'url': measurement.get_detail_url(),
            'lab': {
                'id': unicode(obj.lab.pk),
            },
            'measurement_type': {
                'description': measurement.measurement_type.description,
                'units': measurement.measurement_type.units,
                'measurement_type': measurement.measurement_type.measurement_type
            },
            'description': measurement.description,
            'value': measurement.value
        } for measurement in obj.measurements]
        return doc

    @classmethod
    def get_indexable(cls):
        """Returns the queryset of ids of all things to be indexed.

        Defaults to::

            cls.get_model().objects.order_by('id').values_list(
                'id', flat=True)

        :returns: iterable of ids of objects to be indexed

        """
        return cls.get_model().get_objects()

    @classmethod
    def get_mapping(cls):
        """Returns an Elasticsearch mapping for this MappingType"""
        return {
            "mappings": {
                cls.get_mapping_type_name(): {
                    "properties": {
                        'id': {'type': 'string', 'index': 'not_analyzed'},
                        'lab': {'id': {'type': 'string'}},
                        'measurement_type': {'properties': {'units': 'string', 'description': 'string',
                                                            'measurement_type': 'string', 'analyzer': 'snowball'}},
                    }
                }
            }
        }
