from django.utils import timezone
import random
import factory

from django.utils import lorem_ipsum

from labs.models import Lab
from .models import LabStorage, SFTP


class StorageFactory(factory.DjangoModelFactory):
    FACTORY_FOR = LabStorage

    @factory.lazy_attribute
    def lab(self):
        return Lab.objects.order_by('?')[0]

    @factory.lazy_attribute
    def host(self):
        return 'localhost'

    @factory.lazy_attribute
    def password(self):
        return 'password'

    @factory.lazy_attribute
    def username(self):
        return lorem_ipsum.words(5, False)

    @factory.lazy_attribute
    def type(self):
        return SFTP
