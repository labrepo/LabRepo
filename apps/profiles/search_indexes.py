from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, pre_delete

from elasticutils.contrib.django import MappingType, Indexable

from profiles.models import LabUser
from experiments.search_indexes import ExperimentMappingType


class ProfileMappingType(MappingType, Indexable):
    """
    MappingType for user's profile. Use for search by user's email, first name, last name.
    """
    @classmethod
    def get_model(cls):
        """Returns the Django model this MappingType relates to User"""
        return LabUser

    @classmethod
    def get_mapping_type_name(cls):
        """Returns the name of the mapping.

        By default, this is::

            cls.get_model()._meta.db_table

        Override this if you want to compute the mapping type name
        differently.

        :returns: mapping type string

        """
        return 'profiles_user'

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
            'url': obj.get_absolute_url(),
            'email': obj.email,
            'first_name': obj.first_name or '',
            'last_name': obj.last_name or ''
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
                    }
                }
            }
        }



@receiver(post_save, sender=LabUser)
def update_in_index(sender, instance, **kw):
    from common import tasks
    tasks.create_mapping(ExperimentMappingType)
    tasks.create_mapping(ProfileMappingType)
    # create mapping
    tasks.index_objects.delay(ProfileMappingType, [instance.id])


@receiver(pre_delete, sender=LabUser)
def remove_from_index(sender, instance, **kw):
    from common import tasks
    tasks.unindex_objects.delay(ProfileMappingType, [instance.id])
