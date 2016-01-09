# -*- coding: utf-8 -*-
import json
from django.db import models
from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _, ugettext
from django.db.models.signals import pre_save, post_save, pre_delete
from units.models import Unit
from jsonfield import JSONField
# from history.documents import HistoryDocument


class Measurement(models.Model):
    """
    The model is for storing Measurement data. Bind to Unit

    formats
    headers: [title1, title2, title3]
    table_data: [
       ['a1','a2']
       ['b1','b2']
    ]
    """
    table_data = JSONField(default=[['', '']], verbose_name=_('table data'))
    headers = JSONField(default=['', ''], verbose_name=_('headers'))
    active = models.BooleanField(default=True, verbose_name=_('active'))
    unit = models.OneToOneField(Unit)

    # meta = {'related_fkey_lookups': [], 'local_fields': [], 'virtual_fields': [], 'auto_created': False,
    #         'create_revision_after_save': True, 'versioned': True, 'verbose_name': ugettext('measurement'),
    #         'verbose_name_plural': ugettext('measurements')}

    def __unicode__(self):
        return u'{}'.format(self.headers)

    def get_absolute_url(self):
        unit = self.get_unit()
        if unit:
            return reverse('measurements:list', kwargs={'unit_pk': unit.pk, 'lab_pk': unit.lab.pk})

    def get_detail_url(self):
        unit = self.get_unit()
        if unit:
            return reverse('measurements:detail', kwargs={'unit_pk': unit.pk, 'lab_pk': unit.lab.pk, 'pk': self.pk})

    def get_unit(self):
        from units.models import Unit
        try:
            return Unit.objects.get(measurement=self)
        except Unit.DoesNotExist:
            # todo this should not occur
            return None

    def is_assistant(self, user):
        return self.get_unit().is_assistant(user)

    def is_owner(self, user):
        return self.get_unit().is_owner(user)

    def is_member(self, user):
        return self.get_unit().is_member(user)

    def as_table(self):
        result = []
        result.append(self.headers)
        result.extend(self.table_data)
        return result


Measurement._default_manager = Measurement.objects

# @receiver(me.post_save, sender=MeasurementType)
# def update_unit_index(sender, document, **kw):
#     from units.search_indexes import MeasurementMappingType
#     from common import tasks
#     measurements = MeasurementMappingType.get_model().objects.filter(measurements__measurement_type=document.id)
#     for measurement in measurements:
#         tasks.index_objects.delay(MeasurementMappingType, [measurement.id])
