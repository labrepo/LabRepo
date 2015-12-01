import datetime
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _, ugettext
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from labs.models import Lab


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
    # extra = me.DictField()
    init_user = models.ForeignKey(settings.AUTH_USER_MODEL)
    # instance_type = me.StringField(required=True)
    # object_id = me.ObjectIdField(required=True)
    # instance_type = models.ForeignKey(ContentType)
    # object_id = models.PositiveIntegerField()

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()

    content_object = generic.GenericForeignKey('content_type', 'object_id')
    action_flag = models.IntegerField(choices=ACTION_FLAG)
    action_time = models.DateTimeField(auto_now=True)


    # content_object = me.GenericReferenceField(required=True)

    # meta = {'related_fkey_lookups': [], 'ordering': ['-action_time'], 'virtual_fields': [],
    #         'verbose_name': ugettext('recent activity'), 'verbose_name_plural': ugettext('recent activities')}

    class Meta:
        verbose_name = _('recent activity')
        verbose_name_plural = _('recent activities')
        ordering = ['-action_time']

    def __unicode__(self):
        return '{} {}'.format(self.action_flag, self.instance_type)


# RecentActivity._default_manager = RecentActivity.objects
