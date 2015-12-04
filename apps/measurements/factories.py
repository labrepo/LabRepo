import random
import datetime
from django.utils import lorem_ipsum
import factory

from measurements.models import Measurement


class MeasurementFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Measurement

    @factory.lazy_attribute
    def headers(self):
        return [lorem_ipsum.words(3, False), lorem_ipsum.words(3, False)]

    @factory.lazy_attribute
    def table_data(self):
        return [[float(random.randint(1, 100)), float(random.randint(1, 100))]]


    # @factory.lazy_attribute
    # def measurement_type(self):
    #     return MeasurementTypeFactory(lab=self.lab)
    #
    # @factory.lazy_attribute
    # def created_at(self):
    #     return datetime.datetime.now()


# class MeasurementTypeFactory(factory.DjangoModelFactory):
#     FACTORY_FOR = MeasurementType
#
#     @factory.lazy_attribute
#     def description(self):
#         return lorem_ipsum.words(4, False)
#
#     @factory.lazy_attribute
#     def units(self):
#         return lorem_ipsum.words(5, False)
#
#     @factory.lazy_attribute
#     def measurement_type(self):
#         return lorem_ipsum.words(3, False)
