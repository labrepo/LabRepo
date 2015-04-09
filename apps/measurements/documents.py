# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _, ugettext

import mongoengine as me
from mongoengine.queryset.base import CASCADE

from history.documents import HistoryDocument


class Measurement(HistoryDocument, me.EmbeddedDocument):
    """
    The model is for storing Measurement data. Bind to Unit

    :measurement_type: reference on MeasurementType model
    :type measurement_type: :class:`measurements.documents.MeasurementType`
    """
    created_at = me.DateTimeField(required=True, verbose_name=_('created at'))
    measurement_type = me.ReferenceField('MeasurementType', required=True, verbose_name=_('measurement type'))
    value = me.FloatField(required=True, verbose_name=_('value'))
    description = me.StringField(required=False, verbose_name=_('description'))
    active = me.BooleanField(default=True, verbose_name=_('active'))

    meta = {'related_fkey_lookups': [], 'local_fields': [], 'virtual_fields': [], 'auto_created': False,
            'create_revision_after_save': True, 'versioned': True, 'verbose_name': ugettext('measurement'),
            'verbose_name_plural': ugettext('measurements')}

    def __unicode__(self):
        return u'{}-{}'.format(self.measurement_type, self.value)

    def get_absolute_url(self):
        unit = self.get_unit()
        if unit:
            return reverse('measurements:list', kwargs={'unit_pk': unit.pk, 'lab_pk': unit.lab.pk})

    def get_detail_url(self):
        unit = self.get_unit()
        if unit:
            return reverse('measurements:detail', kwargs={'unit_pk': unit.pk, 'lab_pk': unit.lab.pk, 'pk': self.pk})

    def get_unit(self):
        from units.documents import Unit
        try:
            return Unit.objects.get(measurements___id=self.pk)
        except Unit.DoesNotExist:
            # todo this should not occur
            return None

    def is_assistant(self, user):
        return self.get_unit().is_assistant(user)

    def is_owner(self, user):
        return self.get_unit().is_owner(user)

    def is_member(self, user):
        return self.get_unit().is_member(user)


Measurement._default_manager = Measurement.objects


class MeasurementType(me.Document):
    """
    The model is for storing Measurement type data.
    """
    description = me.StringField(verbose_name=_('description'))
    units = me.StringField(max_length=255, verbose_name=_('the units'))
    measurement_type = me.StringField(unique_with='lab', max_length=255, verbose_name=_('measurement type'))
    lab = me.ReferenceField('Lab', reverse_delete_rule=CASCADE, required=True, verbose_name=_('lab'))
    active = me.BooleanField(default=True, required=True, verbose_name=_('active'))

    meta = {'related_fkey_lookups': [], 'local_fields': [], 'virtual_fields': [], 'verbose_name': ugettext('measurement type'),
            'verbose_name_plural': ugettext('measurements type')}

    def __unicode__(self):
        return u'{}'.format(self.measurement_type)

    def is_assistant(self, user):
        return self.lab.is_assistant(user)

    def is_owner(self, user):
        return self.lab.is_owner(user)

    def is_member(self, user):
        return self.lab.is_member(user)


MeasurementType._default_manager = MeasurementType.objects


@receiver(me.post_save, sender=MeasurementType)
def update_unit_index(sender, document, **kw):
    from units.search_indexes import MeasurementMappingType
    from common import tasks
    measurements = MeasurementMappingType.get_model().objects.filter(measurements__measurement_type=document.id)
    for measurement in measurements:
        tasks.index_objects.delay(MeasurementMappingType, [measurement.id])
