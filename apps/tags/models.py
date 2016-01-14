# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _, ugettext
from django.db import models

from mptt.models import MPTTModel, TreeForeignKey

from labs.models import Lab


class Tag(MPTTModel):
    """
    The model is for storing tag.
    """
    details = models.CharField(max_length=2048, verbose_name=_('details'))
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    color = models.CharField(max_length=2048, verbose_name=_('color'))
    # params = me.DictField(verbose_name=_('params'))
    lab = models.ForeignKey(Lab, verbose_name=_('lab'))

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    def __unicode__(self):
        return u'{}'.format(self.details)

    def get_detail_url(self):
        return reverse('tags:list', kwargs={'lab_pk': self.lab.pk})

    def get_absolute_url(self):
        return reverse('tags:update', kwargs={'pk': self.pk, 'lab_pk': self.lab.pk})