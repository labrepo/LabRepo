from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _, ugettext
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from labs.models import Lab
from experiments.models import Experiment


class RecentActivity(models.Model):
    """
    This will showcase the latest activity that is associated with the user.
    If he is part of a committee, and a new document is added, then this will appear here.
    Title of the activity (New or Updated Documents),
    """
    ADD, UPDATE, DELETE, COMMENT = range(1, 5)
    ACTION_FLAG = (
        (ADD, _('created')),
        (UPDATE, _('updated')),
        (DELETE, _('removed')),
        (COMMENT, _('commented'))
    )
    lab_id = models.ForeignKey(Lab)
    experiments = models.ManyToManyField(Experiment, blank=True)
    value = models.TextField(null=True, blank=True)
    init_user = models.ForeignKey(settings.AUTH_USER_MODEL)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    action_flag = models.IntegerField(choices=ACTION_FLAG)
    action_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('recent activity')
        verbose_name_plural = _('recent activities')
        ordering = ['-action_time']

    def __unicode__(self):
        return '{} {}'.format(self.action_flag, self.content_object)