from django.dispatch import receiver

from elasticutils.contrib.django import MappingType, Indexable
from django.db.models.signals import pre_save, post_save, pre_delete

from .models import Unit


class UnitMappingType(MappingType, Indexable):
    """
    MappingType for units. Use for search by sample and tags
    """
    @classmethod
    def get_model(cls):
        """Returns the Django model this MappingType relates to unit"""
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
        return 'units_unit'

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
            'id': unicode(obj.id),
            'url': obj.get_absolute_url(),
            'sample': obj.sample,
            'lab': {
                'id': unicode(obj.lab.pk),
            },
            'tags': [{'details': tag.details, 'params': tag.params} for tag in obj.tags.all()],
            '_parent': unicode(experiment.pk)} for experiment in obj.experiments.all()]
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
                        'tags': {'properties': {
                            'details': {'type': 'string', 'analyzer': 'snowball'},
                        }},
                    }
                }
            }
        }


@receiver(post_save, sender=Unit)
def update_in_index(sender, instance, **kw):
    from common import tasks
    if instance.active:
        tasks.index_objects.delay(UnitMappingType, [instance.id])
        # for measurement in document.measurements:
        #     tasks.index_objects.delay(MeasurementMappingType, [measurement.id])
    else:
        tasks.unindex_objects.delay(UnitMappingType, [instance.id])
        # tasks.unindex_objects.delay(MeasurementMappingType, [measurement.id for measurement in document.measurements])


@receiver(pre_delete, sender=Unit)
def remove_from_index(sender, instance, **kw):
    from common import tasks
    tasks.unindex_objects.delay(UnitMappingType, [instance.id])
    # tasks.unindex_objects.delay(MeasurementMappingType, [measurement.id for measurement in document.measurements])
