from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from elasticutils.contrib.django import MappingType, Indexable

from .models import Comment


class CommentMappingType(MappingType, Indexable):
    """
    MappingType for comments. Use for search by user's email, and  comment's text.
    """
    @classmethod
    def get_model(cls):
        """Returns the Django model this MappingType relates to comment"""
        return Comment

    @classmethod
    def get_mapping_type_name(cls):
        """Returns the name of the mapping.

        By default, this is::

            cls.get_model()._meta.db_table

        Override this if you want to compute the mapping type name
        differently.

        :returns: mapping type string

        """
        return 'comments_comment'

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
            'init_user': {
                'email': obj.init_user.email
            },
            'text': obj.text,
            'url': obj.get_absolute_url(),
            '_parent': unicode(obj.content_object.pk)   # todo use only experiments pk
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
                    "properties": {
                        'id': {'type': 'string'},
                        'text': {'type': 'string', 'analyzer': 'snowball'},
                    }
                }
            }
        }


@receiver(post_save, sender=Comment)
def update_in_index(sender, instance, **kw):
    from common import tasks
    tasks.index_objects.delay(CommentMappingType, [instance.id])


@receiver(pre_delete, sender=Comment)
def remove_from_index(sender, instance, **kw):
    from common import tasks
    tasks.unindex_objects.delay(CommentMappingType, [instance.id])