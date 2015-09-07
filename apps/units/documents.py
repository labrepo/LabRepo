# -*- coding: utf-8 -*-
from datetime import datetime

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _, ugettext

import mongoengine as me
from mongoengine.queryset.base import CASCADE, DO_NOTHING

from experiments.documents import Experiment
from history.documents import HistoryDocument
from measurements.documents import Measurement
from tags.documents import Tag
from uploader.documents import BaseFile


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
    # files = me.ListField(me.FileField(), verbose_name=_('files'))
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

    @property
    def links(self):
        return UnitLink.objects.filter(parent=self)

Unit._default_manager = Unit.objects


class UnitFile(BaseFile):
    """
    The model is for storing Unit files in GridFS

    :parent: reference on unit
    """
    parent = me.ReferenceField('Unit', reverse_delete_rule=CASCADE, required=True, verbose_name=_('unit'))


UnitFile._default_manager = UnitFile.objects


class UnitLink(me.Document):
    """
    The model is for storing Unit links

    :parent: reference on unit
    """
    parent = me.ReferenceField('Unit', reverse_delete_rule=CASCADE, required=True, verbose_name=_('unit'))
    link = me.URLField(verbose_name=_('url'))
    timestamp = me.DateTimeField(default=datetime.now, required=True)

    def is_assistant(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a assistant of laboratory
        :rtype: bool
        """
        return self.parent.is_owner(user) or self.parent.is_viewer(user) or self.parent.is_member(user)

UnitLink._default_manager = UnitLink.objects