# # -*- coding: utf-8 -*-
# from django.core.urlresolvers import reverse
# from django.utils.translation import gettext_lazy as _, ugettext
# import mongoengine as me
# from mongoengine.queryset.base import CASCADE
# from mongoengine.django.auth import User
#
#
# class LabStorage(me.Document):
#     """
#     Filesystem storage for laboratories
#     """
#     FS_TYPES = (
#         ('SFTP', 'SFTP'),
#         ('s3', 's3'),
#     )
#
#     type = me.StringField(verbose_name=_('type'), choices=FS_TYPES, max_length=255, required=True)
#     readonly = me.BooleanField(verbose_name=_('read only'), default=False)
#     username = me.StringField(verbose_name=_('username'), max_length=255, required=True)
#     host = me.StringField(verbose_name=_('host'), max_length=255, required=True)
#     path = me.StringField(verbose_name=_('path'), max_length=512, required=False)
#     folder_name = me.StringField(verbose_name=_('folder name'), max_length=255, required=False)
#     password = me.StringField(verbose_name=_('password'), max_length=255, required=False)
#     port = me.IntField(verbose_name=_('port'))
#
#     key_file = me.FileField(verbose_name=_('SSH key file'), required=False)
#
#     def get_path(self):
#         if self.path:
#             return self.path
#         else:
#             return u'/home/{}/'.format(self.username)
#
#     def get_folder_name(self):
#         if self.folder_name:
#             return self.folder_name
#         fs_name = u'{}@{}'.format(self.username, self.host)
#         if self.readonly:
#             fs_name += u'(readonly)'
#         return fs_name
#
#     def __unicode__(self):
#         if self.type == 'SFTP':
#             return u'SFTP: {}@{}{}'.format(self.username, self.host, self.get_path())
#         return u'{}'.format(self.name)
#
# LabStorage._default_manager = LabStorage.objects
#
#
# class Lab(me.Document):
#     """
#     Science laboratories
#
#     :name: Title of science laboratory.
#     :investigator: Principal Investigator (PI) is a super user. Can view/edit everything that belong to a Lab.
#     :members: Members are the ordinary users. By default can only see the list of experiments.
#     :guests: Guests can not see the list of experiments (only those experiments they are added to).
#     """
#     name = me.StringField(verbose_name=_('name'), max_length=255, required=True)
#     investigator = me.ListField(me.ReferenceField(User), required=True, verbose_name=_('investigators'))
#     members = me.ListField(me.ReferenceField(User), verbose_name=_('members'))
#     guests = me.ListField(me.ReferenceField(User), verbose_name=_('guests'))
#     is_test = me.BooleanField(default=False, verbose_name=_('test lab'))
#     storages = me.ListField(me.ReferenceField(LabStorage), verbose_name=_('storages'))
#
#     meta = {'related_fkey_lookups': [], 'virtual_fields': [], 'verbose_name': ugettext('lab'), 'verbose_name_plural': ugettext('labs')}
#
#     def __unicode__(self):
#         return u'{}'.format(self.name)
#
#     def get_absolute_url(self):
#         return reverse('labs:detail', kwargs={'lab_pk': self.pk})
#
#     def is_guest(self, user):
#         """
#         :param user: User instance
#         :return: Checks whether the user is a guest
#         :rtype: bool
#         """
#         return user in self.guests
#
#     def is_member(self, user):
#         """
#         :param user: User instance
#         :return: Checks whether the user is a member
#         :rtype: bool
#         """
#         return user in self.members
#
#     def is_owner(self, user):
#         """
#         :param user: User instance
#         :return: Checks whether the user is a principal investigator
#         :rtype: bool
#         """
#         return user in self.investigator
#
#     def is_assistant(self, user):
#         """
#         :param user: User instance
#         :return: Checks whether the user is a assistant of laboratory
#         :rtype: bool
#         """
#         return self.is_guest(user) or self.is_member(user) or self.is_owner(user)
#
#
# Lab._default_manager = Lab.objects
