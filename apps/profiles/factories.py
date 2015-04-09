import factory

from django.contrib.auth.hashers import make_password
from django.contrib.webdesign import lorem_ipsum

from mongoengine.django.auth import User


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User

    @factory.sequence
    def username(n):
        return u'{0}-{1}'.format(lorem_ipsum.words(1, False), n)

    @factory.lazy_attribute_sequence
    def email(self, n):
        return u'{0}-{1}@example.com'.format('admin', n)

    password = make_password('qwerty')

    is_active = True
