# -*- coding: utf-8 -*-
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _, ugettext
from django.db import models
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from comments.search_indexes import CommentMappingType


class Comment(models.Model):
    """
    Model to add comments to every Unit / Experiment / Measurement.
    """
    #TODO
    init_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user')
    instance_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('instance_type', 'object_id')
    action_time = models.DateTimeField(auto_now=True)
    text = models.TextField()

    class Meta:
        verbose_name = _('comment')
        verbose_name_plural = _('comments')
        ordering = ['-action_time']

    def __unicode__(self):
        return u'{}'.format(self.text)

    def get_absolute_url(self):
        return self.get_object().get_absolute_url()

    #TODO
    # def get_object(self):
    #     try:
    #         return get_document(self.instance_type).objects.get(pk=self.object_id)
    #     except DoesNotExist:
    #         return None


@receiver(post_save, sender=Comment)
def update_in_index(sender, instance, **kw):
    from common import tasks
    tasks.index_objects.delay(CommentMappingType, [instance.id])


@receiver(pre_delete, sender=Comment)
def remove_from_index(sender, instance, **kw):
    from common import tasks
    tasks.unindex_objects.delay(CommentMappingType, [instance.id])

