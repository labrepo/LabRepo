# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _, ugettext

from jsonfield import JSONField

from units.models import Unit


class Measurement(models.Model):
    """
    The model is for storing a measurement data. Bind to Unit

    Measurement table format:
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

    def __unicode__(self):
        return u'{}'.format(self.headers)

    def get_absolute_url(self):
            return reverse('measurements:list', kwargs={'unit_pk': self.unit.pk, 'lab_pk': self.unit.lab.pk})

    def is_assistant(self, user):
        return self.unit.is_assistant(user)

    def is_owner(self, user):
        return self.unit.is_owner(user)

    def is_member(self, user):
        return self.unit.is_member(user)

    def as_table(self):
        """Concat headers and table data to a hadsontable representation."""
        result = list()
        result.append(self.headers)
        result.extend(self.table_data)
        return result