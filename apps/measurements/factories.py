import random

from django.utils import lorem_ipsum

import factory

from .models import Measurement


class MeasurementFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Measurement

    @factory.lazy_attribute
    def headers(self):
        return [lorem_ipsum.words(3, False), lorem_ipsum.words(3, False)]

    @factory.lazy_attribute
    def table_data(self):
        return [[float(random.randint(1, 100)), float(random.randint(1, 100))]]