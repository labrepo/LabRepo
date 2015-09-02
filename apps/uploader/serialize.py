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
    url = reverse('upload:file-download', kwargs={  #TODO: add app label
        'lab_pk': lab_pk,
        'document_name': instance._class_name,
        'pk': instance.pk})

    delete_url = reverse('upload:file-delete', kwargs={  #TODO: add app label
        'lab_pk': lab_pk,
        'document_name': instance._class_name,
        'pk': instance.pk})

    return {
        'url': url,
        'name': instance.name,
        'type': instance.content_type,
        # 'thumbnailUrl': obj.url,
        'size': instance.size,
        'deleteUrl': delete_url,
        'deleteType': 'DELETE',
    }

