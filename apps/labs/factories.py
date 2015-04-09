import factory

from django.contrib.webdesign import lorem_ipsum
from mongoengine.django.auth import User

from labs.documents import Lab


class LabFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Lab

    @factory.lazy_attribute
    def name(self):
        return lorem_ipsum.words(5, False)

    @factory.lazy_attribute
    def owners(self):
        return User.objects.order_by('?')[0]

