from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, pre_delete

from .models import Tag


@receiver(post_save, sender=Tag)
def update_unit_index(sender, instance, **kw):
    from units.search_indexes import UnitMappingType
    from common import tasks
    units = UnitMappingType.get_model().objects.filter(tags=instance.id)
    for unit in units:
        tasks.index_objects.delay(UnitMappingType, [unit.id])