from django.contrib.webdesign import lorem_ipsum
import factory

from experiments.documents import Experiment
from labs.documents import Lab
from measurements.factories import MeasurementFactory
from tags.factories import TagFactory
from units.documents import Unit


class UnitFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Unit

    @factory.lazy_attribute
    def parent(self):
        return []

    @factory.lazy_attribute
    def measurements(self):
        return MeasurementFactory.create_batch(2, lab=self.lab, user=self.user)

    @factory.lazy_attribute
    def experiments(self):
        return [Experiment.objects.order_by('?')[0]]

    @factory.lazy_attribute
    def lab(self):
        return Lab.objects.order_by('?')[0]

    @factory.lazy_attribute
    def sample(self):
        return lorem_ipsum.words(1, False)

    @factory.lazy_attribute
    def tags(self):
        return [TagFactory()]
