import factory

from django.utils import lorem_ipsum

from labs.models import Lab
from measurements.factories import MeasurementFactory
from units.models import Unit


class UnitFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Unit

    @factory.lazy_attribute
    def measurements(self):
        return MeasurementFactory()
        # return MeasurementFactory(lab=self.lab, user=self.user)

    @factory.lazy_attribute
    def lab(self):
        return Lab.objects.order_by('?')[0]

    @factory.lazy_attribute
    def sample(self):
        return lorem_ipsum.words(1, False)

    @factory.post_generation
    def experiments(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for experiment in extracted:
                self.experiments.add(experiment)