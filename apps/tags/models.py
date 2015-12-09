# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, pre_delete
from django.utils.translation import ugettext_lazy as _, ugettext
from django.db import models

from mptt.models import MPTTModel, TreeForeignKey

from labs.models import Lab


class Tag(MPTTModel):
    """
    The model is for storing tag.
    """
    details = models.CharField(max_length=2048, verbose_name=_('details'))
    # parent = me.ReferenceField('self', reverse_delete_rule=CASCADE, verbose_name=_('parent'))
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    color = models.CharField(max_length=2048, verbose_name=_('color'))
    # params = me.DictField(verbose_name=_('params'))
    lab = models.ForeignKey(Lab, verbose_name=_('lab'))

    # meta = {'related_fkey_lookups': [], 'local_fields': [], 'virtual_fields': [],
    #         'indexes': [
    #             {'fields': ['details', 'lab', 'parent'], 'unique': True},
    #         ], 'verbose_name': ugettext('tag'), 'verbose_name_plural': ugettext('tags')}

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    def __unicode__(self):
        return u'{}'.format(self.details)

    def get_detail_url(self):
        return reverse('tags:list', kwargs={'lab_pk': self.lab.pk})

    def get_absolute_url(self):
        return reverse('tags:update', kwargs={'pk': self.pk, 'lab_pk': self.lab.pk})

    # def get_children(self):
    #     return self.children(self, [])
    #
    # def children(self, tag, all_child=[]):
    #     all_child.append(tag)
    #     for child in self.__class__.objects.filter(parent__in=[tag]):
    #         all_child.extend(self.children(child, []))
    #     return all_child


Tag._default_manager = Tag.objects


@receiver(post_save, sender=Tag)
def update_unit_index(sender, instance, **kw):
    from units.search_indexes import UnitMappingType
    from common import tasks
    units = UnitMappingType.get_model().objects.filter(tags=instance.id)
    for unit in units:
        tasks.index_objects.delay(UnitMappingType, [unit.id])