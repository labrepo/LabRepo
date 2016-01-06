# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _, ugettext
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Comment(models.Model):
    """
    Model to add comments to every Unit / Experiment.
    """
    init_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user')
    instance_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('instance_type', 'object_id')
    action_time = models.DateTimeField(auto_now=True)
    text = models.TextField()

    class Meta:
        verbose_name = _('comment')
        verbose_name_plural = _('comments')
        ordering = ['-action_time']

    def __unicode__(self):
        return self.text

    def get_absolute_url(self):
        return self.content_object.get_absolute_url()
