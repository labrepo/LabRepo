# -*- coding: utf-8 -*-
import datetime

from django.dispatch import receiver
from django.utils.translation import ugettext

import mongoengine as me
from mongoengine.base.common import get_document
from mongoengine.django.auth import User
from mongoengine.errors import DoesNotExist
from mongoengine import post_save, pre_delete

from comments.search_indexes import CommentMappingType


class Comment(me.Document):
    """
    Model to add comments to every Unit / Experiment / Measurement.
    """
    init_user = me.ReferenceField(User, required=True)
    instance_type = me.StringField(required=True)
    object_id = me.ObjectIdField(required=True)
    action_time = me.DateTimeField(default=datetime.datetime.now, required=True)
    text = me.StringField(required=True)

    meta = {'related_fkey_lookups': [], 'virtual_fields': [], 'verbose_name': ugettext('comment'),
            'verbose_name_plural': ugettext('comments')}

    class Meta:
        ordering = ['-action_time']

    def __unicode__(self):
        return u'{}'.format(self.text)

    def get_absolute_url(self):
        return self.get_object().get_absolute_url()

    def get_object(self):
        try:
            return get_document(self.instance_type).objects.get(pk=self.object_id)
        except DoesNotExist:
            return None

Comment._default_manager = Comment.objects

@receiver(post_save, sender=Comment)
def update_in_index(sender, document, **kw):
    from common import tasks
    tasks.index_objects.delay(CommentMappingType, [document.id])


@receiver(pre_delete, sender=Comment)
def remove_from_index(sender, document, **kw):
    from common import tasks
    tasks.unindex_objects.delay(CommentMappingType, [document.id])
