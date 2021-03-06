import factory

from django.utils import lorem_ipsum

from labs.models import Lab
from measurements.factories import MeasurementFactory
from .models import Unit


class UnitFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Unit

    @factory.lazy_attribute
    def lab(self):
        return Lab.objects.order_by('?')[0]

    @factory.lazy_attribute
    def sample(self):
        return lorem_ipsum.words(1, False)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for tag in extracted:
                self.tags.add(tag)

    @factory.post_generation
    def experiments(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for experiment in extracted:
                self.experiments.add(experiment)