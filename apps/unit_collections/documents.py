# -*- coding: utf-8 -*-

import mongoengine as me
from mongoengine.django.auth import User
from mongoengine.queryset.base import CASCADE

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _, ugettext

from units.documents import Unit


class Collection(me.Document):
    """
    The model is for storing collection data.

    :lab: reference on laboratory
    :type lab: :class:`labs.documents.Lab`
    :title: collection name
    :units: list of units in collection
    :owners: super users for this collection
    :editors: can edit data, cans delete or edit info of the collection.
    :viewers: can only browse data. can't edit
    """
    lab = me.ReferenceField('Lab', reverse_delete_rule=CASCADE, required=True, verbose_name=_('lab'))
    title = me.StringField(required=True, max_length=255, verbose_name=_('title'))
    units = me.ListField(me.ReferenceField(Unit), required=True, verbose_name=_('units'))
    owners = me.ListField(me.ReferenceField(User), required=True, verbose_name=_('owners'))
    editors = me.ListField(me.ReferenceField(User), verbose_name=_('editors'))
    viewers = me.ListField(me.ReferenceField(User), verbose_name=_('viewers'))
    description = me.StringField(required=False, verbose_name=_('description'))

    meta = {'related_fkey_lookups': [], 'virtual_fields': [],
            'verbose_name': ugettext('collection'), 'verbose_name_plural': ugettext('collections')}

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('collections:update', kwargs={'lab_pk': self.lab.pk, 'pk': self.pk})

    def is_owner(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a owner
        :rtype: bool
        """
        return self.lab.is_owner(user) or user in self.owners

    def is_editor(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a editor
        :rtype: bool
        """
        return user in self.editors

    def is_viewer(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a viewer
        :rtype: bool
        """
        for unit in self.units:
            if unit.is_viewer(user) and unit.active:
                return True
        return user in self.viewers

    def is_assistant(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a assistant of laboratory
        :rtype: bool
        """
        return self.is_owner(user) or self.is_viewer(user) or self.is_editor(user)


Collection._default_manager = Collection.objects