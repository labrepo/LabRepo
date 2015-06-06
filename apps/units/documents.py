# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _, ugettext

import mongoengine as me
from mongoengine.queryset.base import CASCADE, DO_NOTHING

from experiments.documents import Experiment
from history.documents import HistoryDocument
from measurements.documents import Measurement
from tags.documents import Tag


class Unit(HistoryDocument):
    """
    The model is for storing Unit data. Bind to laboratory

    :lab: reference on laboratory
    :type lab: :class:`labs.documents.Lab`
    :experiments: reference on experiments
    :type experiments: :class:`experiments.documents.Experiment`
    :parent: reference on itself. Need for define SubUnit
    :measurement: reference to model :class:`measurements.documents.Measurement`
    :tags: reference to model :class:`tags.documents.tags`
    """
    lab = me.ReferenceField('Lab', reverse_delete_rule=CASCADE, required=True, verbose_name=_('lab'))
    experiments = me.ListField(me.ReferenceField(Experiment, reverse_delete_rule=CASCADE), required=True, verbose_name=_('experiments'))
    parent = me.ListField(me.ReferenceField('self', reverse_delete_rule=DO_NOTHING), verbose_name=_('parent'))
    sample = me.StringField(required=True, verbose_name=_('sample'))
    tags = me.ListField(me.ReferenceField(Tag), required=False, verbose_name=_('tags'))
    active = me.BooleanField(default=True, verbose_name=_('active'))
    # measurements = me.ListField(me.EmbeddedDocumentField(Measurement), verbose_name=_('measurements'))
    measurements = me.EmbeddedDocumentField(Measurement)
    description = me.StringField(required=False, verbose_name=_('description'))

    meta = {'create_revision_after_save': True, 'versioned': True, 'related_fkey_lookups': [], 'local_fields': [],
            'virtual_fields': [], 'auto_created': False, 'verbose_name': ugettext('unit'), 'verbose_name_plural': ugettext('units')}

    def __unicode__(self):
        return u"{}".format(self.sample)

    def get_absolute_url(self):
        return reverse('units:detail', kwargs={'pk': self.pk, 'lab_pk': self.lab.pk})

    def is_owner(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a owner
        :rtype: bool
        """
        for experiment in self.experiments:
            if experiment.is_owner(user) or experiment.is_editor(user):
                return True
        return self.lab.is_owner(user)

    def is_member(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a lab's member
        :rtype: bool
        """
        return self.lab.is_member(user)

    def is_viewer(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a viewer
        :rtype: bool
        """
        for experiment in self.experiments:
            if experiment.is_viewer(user):
                return True
        from unit_collections.documents import Collection
        for collection in Collection.objects.filter(units__in=[self]):
            if collection.is_owner(user) or collection.is_editor(user) and user in collection.viewers:
                return True
        return self.lab.is_owner(user)# or self.lab.is_member(user)

    def is_assistant(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a assistant of laboratory
        :rtype: bool
        """
        return self.is_owner(user) or self.is_viewer(user) or self.is_member(user)


Unit._default_manager = Unit.objects
