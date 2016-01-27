# encoding: utf-8
import re

from django.core.urlresolvers import reverse
from django.utils import formats


def order_name(name):
    """order_name -- Limit a text to 20 chars length, if necessary strips the
    middle of the text and substitute it for an ellipsis.

    name -- text to be limited.

    """
    name = re.sub(r'^.*/', '', name)
    if len(name) <= 20:
        return name
    return name[:10] + "..." + name[-7:]


def get_short_name(name):
    if len(name) > 25:
        return name[:20] + u'...' + name[-3:]
    return name


def serialize(instance, lab_pk):
    """serialize -- Serialize a file doc instance into a dict.

    instance -- File doc instance
    """
    if instance.file:
        url = instance.file.url
    else:
        url = instance.outer_url

    if instance.thumbnail:
        thumbnail_url = instance.thumbnail.url
    else:
        thumbnail_url = instance.get_outer_thumb()

    delete_url = reverse('upload:file-delete', kwargs={
        'lab_pk': lab_pk,
        'app_name': instance.__class__._meta.app_label,
        'model_name': instance.__class__.__name__,
        'pk': instance.pk
    })

    return {
        'url': url,
        'name': instance.filename,
        'short_name': get_short_name(instance.filename),
        'type': instance.content_type,
        'thumbnailUrl': thumbnail_url,
        'size': instance.file.size,
        'timestamp': formats.date_format(instance.timestamp, "DATE_FORMAT"),
        'deleteUrl': delete_url,
        'deleteType': 'DELETE',
    }

