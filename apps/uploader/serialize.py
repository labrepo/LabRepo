# encoding: utf-8
import re
from django.core.urlresolvers import reverse


def order_name(name):
    """order_name -- Limit a text to 20 chars length, if necessary strips the
    middle of the text and substitute it for an ellipsis.

    name -- text to be limited.

    """
    name = re.sub(r'^.*/', '', name)
    if len(name) <= 20:
        return name
    return name[:10] + "..." + name[-7:]


def serialize(instance, lab_pk):
    """serialize -- Serialize a file doc instance into a dict.

    instance -- File doc instance
    """
    if instance.file:
        url = reverse('upload:file-download', kwargs={  #TODO: add app label
            'lab_pk': lab_pk,
            'document_name': instance._class_name,
            'pk': instance.pk})
    else:
        url = instance.outer_url

    if instance.thumbnail:
        thumbnail_url = reverse('upload:file-thumb', kwargs={  #TODO: add app label
            'lab_pk': lab_pk,
            'document_name': instance._class_name,
            'file_name': instance.name,
            'pk': instance.pk})
    else:
        thumbnail_url = instance.get_outer_thumb()

    delete_url = reverse('upload:file-delete', kwargs={  #TODO: add app label
        'lab_pk': lab_pk,
        'document_name': instance._class_name,
        'pk': instance.pk})

    return {
        'url': url,
        'name': instance.name,
        'type': instance.content_type,
        'thumbnailUrl': thumbnail_url,
        'size': instance.size,
        'deleteUrl': delete_url,
        'deleteType': 'DELETE',
    }

