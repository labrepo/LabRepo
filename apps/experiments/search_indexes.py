# -*- coding: utf-8 -*-
from django.dispatch import receiver

from elasticutils.contrib.django import MappingType, Indexable
from mongoengine import post_save, pre_delete

from experiments.documents import Experiment


class ExperimentMappingType(MappingType, Indexable):
    """
    MappingType for experiments. Use for search by experiment's description, title,
    owners (email, first name, last name), editors (email, first name, last name),
    viewers (email, first name, last name), lab's investigator (email, first name, last name),
    lab's members (email, first name, last name),  lab's guests (email, first name, last name).
    """
    @classmethod
    def get_model(cls):
        """Returns the Django model this MappingType relates to experiment"""
        return Experiment

    @classmethod
    def get_mapping_type_name(cls):
        """Returns the name of the mapping.

        By default, this is::

            cls.get_model()._meta.db_table

        Override this if you want to compute the mapping type name
        differently.

        :returns: mapping type string

        """
        return 'experiments_experiment'

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
        return {
            'id': unicode(obj.id),
            'description': obj.description,
            'title': obj.title,
            'url': obj.get_absolute_url(),
            'owners': [{'email': user.email,
                        'first_name': user.first_name or '',
                        'last_name': user.last_name or ''} for user in obj.owners],
            'editors': [{'email': user.email,
                         'first_name': user.first_name or '',
                         'last_name': user.last_name or ''} for user in obj.editors],
            'viewers': [{'email': user.email,
                         'first_name': user.first_name or '',
                         'last_name': user.last_name or ''} for user in obj.viewers],
            'lab': {
                'id': unicode(obj.lab.pk),
                'investigator': [{'email': user.email,
                                  'first_name': user.first_name or '',
                                  'last_name': user.last_name or ''} for user in obj.lab.investigator],
                'members': [{'email': user.email,
                             'first_name': user.first_name or '',
                             'last_name': user.last_name or ''} for user in obj.lab.members],
                'guests': [{'email': user.email,
                            'first_name': user.first_name or '',
                            'last_name': user.last_name or ''} for user in obj.lab.guests],
            },
        }

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
                    "_all": {"enabled": True},
                    "properties": {
                        "id": {
                            "type": "string"
                        },
                        "description": {
                            "type": "string",
                            'analyzer': 'snowball'
                        }
                    }
                },
                'comments_comment': {
                    "_all": {"enabled": True},
                    '_parent': {
                        'type': cls.get_mapping_type_name()
                    }
                },
                'units_unit': {
                    "_all": {"enabled": True},
                    '_parent': {
                        'type': cls.get_mapping_type_name()
                    }
                },
                'measurements_measurement': {
                    "_all": {"enabled": True},
                    '_parent': {
                        'type': 'units_unit'
                    }
                }
            }
        }


@receiver(post_save, sender=Experiment)
def update_in_index(sender, document, **kw):
    from common import tasks
    if document.active:
        tasks.index_objects.delay(ExperimentMappingType, [document.id])
    else:
        tasks.unindex_objects.delay(ExperimentMappingType, [document.id])


@receiver(pre_delete, sender=Experiment)
def remove_from_index(sender, document, **kw):
    from common import tasks
    tasks.unindex_objects.delay(ExperimentMappingType, [document.id])
