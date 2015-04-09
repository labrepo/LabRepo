import random
import factory

from django.contrib.webdesign import lorem_ipsum
from mongoengine.django.auth import User

from labs.documents import Lab
from .documents import Collection
from units.documents import Unit


class CollectionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Collection

    @factory.lazy_attribute
    def units(self):
        units = Unit.objects.filter(lab=self.lab).order_by('?')
        return units[:units.count() - random.randint(0, units.count() - 1)]

    @factory.lazy_attribute
    def lab(self):
        return Lab.objects.order_by('?')[0]

    @factory.lazy_attribute
    def title(self):
        return lorem_ipsum.words(1, False)

    @factory.lazy_attribute
    def owners(self):
        return User.objects.order_by('?')[0]
