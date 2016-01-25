from django.db.models import BLANK_CHOICE_DASH
from django.http import Http404
from django.db.models.query import QuerySet
from django.utils.encoding import smart_text

from profiles.models import LabUser as User


def create_test_lab(self):
    from labs.models import Lab
    from experiments.models import Experiment
    from comments.models import Comment
    # from measurements.models import Measurement, MeasurementType
    from units.models import Unit
    from tags.models import Tag

    try:
        lab = Lab.objects.get(is_test=True)
    except Lab.DoesNotExist:
        lab = None
    if lab:
        base_lab_id = lab.pk
        user = self
        lab.pk = None
        lab.save()
        lab.investigator = [user]
        lab.members = []
        lab.guests = []
        lab.is_test = False
        lab.save()
        experiments, measurement_types, tags = {}, {}, {}
        # for measurement_type in MeasurementType.objects.filter(lab=base_lab_id):
        #     base_measurement_type = measurement_type.pk
        #     measurement_type.lab = lab
        #     measurement_type.pk = None
        #     measurement_type = measurement_type.save()
        #     measurement_types[unicode(base_measurement_type)] = measurement_type

        for tag in Tag.objects.filter(lab=base_lab_id).order_by('-parent'):
            base_tag = tag.pk
            tag.lab = lab
            tag.pk = None
            tag.save()
            tags[unicode(base_tag)] = tag
            Tag.objects.filter(lab=lab, parent=base_tag).update(parent=tag)

        for experiment in Experiment.objects.filter(lab__pk=base_lab_id):
            base_experiment = experiment.pk
            experiment.lab = lab
            experiment.pk = None
            experiment.save()
            experiment.editors = []
            experiment.viewers = []
            experiment.owners = [user]
            experiment.save()

            experiments[unicode(base_experiment)] = experiment
            for comment in Comment.objects.filter(object_id=base_experiment):
                comment.object_id = experiment.pk
                comment.pk = None
                comment.save()

        for unit in Unit.objects.filter(lab__pk=base_lab_id):
            unit_experiments = unit.experiments.all()
            base_unit = unit.pk
            unit.lab = lab
            unit.pk = None
            unit.save()
            unit_experiment = []
            for experiment in unit_experiments:
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
            for tag in unit.tags.all():
                unit_tags.append(tags[unicode(tag.pk)])
            unit.tags = unit_tags
            unit.save()
            for comment in Comment.objects.filter(object_id=base_unit):
                comment.object_id = unit.pk
                comment.pk = None
                comment.save()
        return lab

# User.add_to_class('full_name', full_name)
# User.add_to_class('get_absolute_url', get_absolute_url)
# User.add_to_class('has_usable_password', has_usable_password)
User.add_to_class('create_test_lab', create_test_lab)
# User._meta['virtual_fields'] = []



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
