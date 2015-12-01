# import datetime
#
# from django.utils.translation import gettext_lazy as _, ugettext
# import mongoengine as me
# from mongoengine.django.auth import User
#
#
# class RecentActivity(me.Document):
#     """
#     This will showcase the latest activity that is associated with the user.
#     If he is part of a committee, and a new document is added, then this will appear here.
#     Title of the activity (New or Updated Documents),
#     """
#     ADD, UPDATE, DELETE, COMMENT = range(1, 5)
#     ACTION_FLAG = (
#         (ADD, _('created')),
#         (UPDATE, _('updated')),
#         (DELETE, _('removed')),
#         (COMMENT, _('commented'))
#     )
#     lab_id = me.StringField(required=True)
#     extra = me.DictField()
#     init_user = me.ReferenceField(User, required=True)
#     instance_type = me.StringField(required=True)
#     object_id = me.ObjectIdField(required=True)
#     action_flag = me.IntField(choices=ACTION_FLAG, required=True)
#     action_time = me.DateTimeField(default=datetime.datetime.now, required=True)
#     content_object = me.GenericReferenceField(required=True)
#
#     meta = {'related_fkey_lookups': [], 'ordering': ['-action_time'], 'virtual_fields': [],
#             'verbose_name': ugettext('recent activity'), 'verbose_name_plural': ugettext('recent activities')}
#
#     def __unicode__(self):
#         return '{} {}'.format(self.action_flag, self.instance_type)
#
#
# RecentActivity._default_manager = RecentActivity.objects
