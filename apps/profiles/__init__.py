from django.dispatch import receiver
from django.contrib.auth.hashers import is_password_usable
from django.core.urlresolvers import reverse
from django.db.models import BLANK_CHOICE_DASH
from django.http import Http404
from django.db.models.query import QuerySet
from django.utils.encoding import smart_text
from django.db.models.signals import pre_save, post_save, pre_delete
from django.contrib.auth.models import User

from profiles.models import LabUser as User
from experiments.search_indexes import ExperimentMappingType
from profiles.search_indexes import ProfileMappingType


@property
def full_name(self):
    if self.first_name or self.last_name:
        return self.get_full_name()
    return self.username


def has_usable_password(self):
    return is_password_usable(self.password)


def get_absolute_url(self):
    return reverse('profiles:detail', kwargs={'pk': self.pk})


def create_test_lab(self):
    from labs.models import Lab
    from experiments.models import Experiment
    from comments.models import Comment
    from measurements.models import Measurement, MeasurementType
    from units.models import Unit
    from tags.models import Tag

    try:
        lab = Lab.objects.get(is_test=True)
    except Lab.DoesNotExist:
        lab = None
    if lab:
        base_lab_id = lab.pk
        user = self

        lab.investigator = [user]
        lab.members = []
        lab.guests = []
        lab.pk = None
        lab.is_test = False
        lab = lab.save()

        experiments, measurement_types, tags = {}, {}, {}
        for measurement_type in MeasurementType.objects.filter(lab=base_lab_id):
            base_measurement_type = measurement_type.pk
            measurement_type.lab = lab
            measurement_type.pk = None
            measurement_type = measurement_type.save()
            measurement_types[unicode(base_measurement_type)] = measurement_type

        for tag in Tag.objects.filter(lab=base_lab_id).order_by('-parent'):
            base_tag = tag.pk
            tag.lab = lab
            tag.pk = None
            tag = tag.save()
            tags[unicode(base_tag)] = tag
            Tag.objects.filter(lab=lab, parent=base_tag).update(set__parent=tag)

        for experiment in Experiment.objects.filter(lab=base_lab_id):
            base_experiment = experiment.pk
            experiment.lab = lab
            experiment.pk = None
            experiment.editors = []
            experiment.viewers = []
            experiment.owners = [user]
            experiment = experiment.save(user=user)
            experiments[unicode(base_experiment)] = experiment
            for comment in Comment.objects.filter(object_id=base_experiment):
                comment.object_id = experiment.pk
                comment.pk = None
                comment.save()

        for unit in Unit.objects.filter(lab=base_lab_id):
            base_unit = unit.pk
            unit.lab = lab
            unit.pk = None
            unit_experiment = []
            for experiment in unit.experiments:
                unit_experiment.append(experiments[unicode(experiment.pk)])
            unit.experiments = unit_experiment
            # measurements = []
            # for measurement_pk in unit.measurements:
            #     measurement = Measurement.objects.get(pk=measurement_pk.pk)
            #     measurement.measurement_type = measurement_types[unicode(measurement_pk.measurement_type.pk)]
            #     measurement.pk = None
            #     measurement = measurement.save(user=user)
            #     measurements.append(measurement)
            #     for comment in Comment.objects.filter(object_id=measurement_pk.pk):
            #         comment.object_id = measurement.pk
            #         comment.pk = None
            #         comment.save()
            # unit.measurements = measurements
            unit_tags = []
            for tag in unit.tags:
                unit_tags.append(tags[unicode(tag.pk)])
            unit.tags = unit_tags
            unit = unit.save(user=user)
            for comment in Comment.objects.filter(object_id=base_unit):
                comment.object_id = unit.pk
                comment.pk = None
                comment.save()
        return lab

# User.add_to_class('full_name', full_name)
# User.add_to_class('get_absolute_url', get_absolute_url)
# User.add_to_class('has_usable_password', has_usable_password)
# User.add_to_class('create_test_lab', create_test_lab)
# User._meta['virtual_fields'] = []


@receiver(post_save, sender=User)
def update_in_index(sender, instance, **kw):
    from common import tasks
    tasks.create_mapping(ExperimentMappingType)
    tasks.create_mapping(ProfileMappingType)
    # create mapping
    tasks.index_objects.delay(ProfileMappingType, [instance.id])


@receiver(pre_delete, sender=User)
def remove_from_index(sender, instance, **kw):
    from common import tasks
    tasks.unindex_objects.delay(ProfileMappingType, [instance.id])


def get_related_field(self):
    return self.to._meta.pk


def get_choices(self, include_blank=True, blank_choice=BLANK_CHOICE_DASH):
    """Returns choices with a default blank choices included, for use
    as SelectField choices for this field."""
    first_choice = blank_choice if include_blank else []
    if self.choices:
        return first_choice + list(self.choices)
    rel_model = self.rel.to
    if hasattr(self.rel, 'get_related_field'):
        lst = [(getattr(x, self.rel.get_related_field().attname),
                    smart_text(x))
               for x in rel_model._default_manager.filter(
                   self.rel.limit_choices_to)]
    else:
        lst = [(x._get_pk_val(), smart_text(x))
               for x in rel_model._default_manager.filter(
                   self.rel.limit_choices_to)]
    return first_choice + lst


def distinct(self, field=None):
    if field is None:
        return self
    return super(QuerySet, self).distinct(field)


def values_list(self, *fields, **kwargs):
    return super(QuerySet, self).values_list(*fields)


# Relation.get_related_field = get_related_field
# ReferenceField.get_choices = get_choices
# ReferenceField.null = False  # todo change
# QuerySet.ordered = True
# QuerySet.distinct = distinct
# QuerySet.values_list = values_list
