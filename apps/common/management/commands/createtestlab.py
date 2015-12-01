"""
Management utility to create test lab.
"""
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from experiments.factories import ExperimentFactory
from labs.models import Lab
from labs.factories import LabFactory
from measurements.factories import MeasurementTypeFactory
from profiles.factories import UserFactory
from tags.factories import TagFactory
from units.factories import UnitFactory


class Command(BaseCommand):

    help = 'Used to create a test lab.'

    def handle(self, *args, **options):
        if not Lab.objects.filter(is_test=True):
            owner = UserFactory()
            member = UserFactory()
            guest = UserFactory()
            lab = LabFactory(investigator=[owner.pk], members=[member.pk], guests=[guest.pk], is_test=True)
            experiment1 = ExperimentFactory(lab=lab, owners=[owner.pk], editors=[guest.pk])
            experiment2 = ExperimentFactory(lab=lab, owners=[guest.pk], editors=[owner.pk])
            experiment3 = ExperimentFactory(lab=lab, owners=[member.pk], editors=[owner.pk])
            tag1 = TagFactory(lab=lab)
            tag2 = TagFactory(lab=lab, parent=tag1)
            tag3 = TagFactory(lab=lab, parent=tag2)
            tag4 = TagFactory.create_batch(10, lab=lab)
            tag5 = TagFactory.create_batch(5, lab=lab, parent=tag3)
            tag6 = TagFactory.create_batch(4, lab=lab, parent=tag2)
            TagFactory.create_batch(2, lab=lab, parent=tag2)
            UnitFactory(lab=lab, experiments=[experiment1,experiment2, experiment3], user=owner, tag=tag4)
            UnitFactory(lab=lab, experiments=[experiment2], user=guest, tag=tag4+tag5+[tag3]+[tag2]+[tag1])
            UnitFactory(lab=lab, experiments=[experiment3], user=member, tag=tag4+tag6+[tag2]+[tag1])
            MeasurementTypeFactory.create_batch(2, lab=lab)
            self.stdout.write("Test lab created successfully.")
            return
        self.stdout.write("Test lab already created.")