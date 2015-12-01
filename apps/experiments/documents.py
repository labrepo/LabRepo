# # -*- coding: utf-8 -*-
#
# import mongoengine as me
# from mongoengine.django.auth import User
# from mongoengine.queryset.base import CASCADE
#
# from django.core.urlresolvers import reverse
# from django.utils.translation import ugettext_lazy as _, ugettext
#
# from labs.documents import Lab
#
#
# class Experiment(me.Document):
#     """
#     The model is for storing Laboratory data.
#     To have any role in an experiment, user should belong to the lab this experiment belongs to
#     (at least on Guest privileges).
#
#     :lab: reference on laboratory
#     :type lab: :class:`labs.documents.Lab`
#     :owners: super users for this experiments
#     :editors: can edit data, cans delete or edit info of the experiment.
#     :viewers: can only browse data. can't edit
#     :status: list of values - `Planned`, `In Progress`, `Completed`
#     """
#
#     PLANNED, IN_PROGRESS, COMPLETED = range(1, 4)
#     STATUS = (
#         (PLANNED, _("Planned")),
#         (IN_PROGRESS, _("In Progress")),
#         (COMPLETED, _("Completed"))
#     )
#
#     lab = me.ReferenceField(Lab, reverse_delete_rule=CASCADE, required=True, verbose_name=_('lab'))
#     title = me.StringField(required=True, max_length=255, verbose_name=_('title'))
#     owners = me.ListField(me.ReferenceField(User), required=True, verbose_name=_('owners'))
#     editors = me.ListField(me.ReferenceField(User), verbose_name=_('editors'))
#     viewers = me.ListField(me.ReferenceField(User), verbose_name=_('viewers'))
#     start = me.DateTimeField(required=True, verbose_name=_('start'))
#     end = me.DateTimeField(required=True, verbose_name=_('end'))
#     description = me.StringField(required=False, verbose_name=_('description'))
#     status = me.IntField(choices=STATUS, verbose_name=_('status'))
#     active = me.BooleanField(default=True, required=True, verbose_name=_('active'))
#     wooflo_key = me.StringField(max_length=255, verbose_name=_('wooflo project key'))
#
#     meta = {'related_fkey_lookups': [], 'virtual_fields': [],
#             'verbose_name': ugettext('experiment'), 'verbose_name_plural': ugettext('experiments')}
#
#     def __unicode__(self):
#         return self.title
#
#     def get_absolute_url(self):
#         return reverse('experiments:detail', kwargs={'lab_pk': self.lab.pk, 'pk': self.pk})
#
#     def is_owner(self, user):
#         """
#         :param user: User instance
#         :return: Checks whether the user is a owner
#         :rtype: bool
#         """
#         return user in self.owners or self.lab.is_owner(user)
#
#     def is_member(self, user):
#         """
#         :param user: User instance
#         :return: Checks whether the user is a lab's member
#         :rtype: bool
#         """
#         return self.lab.is_member(user)
#
#     def is_editor(self, user):
#         """
#         :param user: User instance
#         :return: Checks whether the user is a editor
#         :rtype: bool
#         """
#         return user in self.editors
#
#     def is_viewer(self, user):
#         """
#         :param user: User instance
#         :return: Checks whether the user is a viewer
#         :rtype: bool
#         """
#         return user in self.viewers
#
#     def is_experiment_assistant(self, user):
#         """
#         :param user: User instance
#         :return: Checks whether the user is a assistant of experiment
#         :rtype: bool
#         """
#         return self.is_owner(user) or self.is_editor(user) or self.is_viewer(user)
#
#     def is_assistant(self, user):
#         """
#         :param user: User instance
#         :return: Checks whether the user is a assistant of laboratory
#         :rtype: bool
#         """
#         return self.is_experiment_assistant(user) or self.is_member(user)
#
# Experiment._default_manager = Experiment.objects