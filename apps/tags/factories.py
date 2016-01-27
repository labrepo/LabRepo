import json
import factory

from django.utils import lorem_ipsum

from labs.models import Lab
from .models import Tag


class TagFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Tag

    @factory.lazy_attribute
    def details(self):
        return lorem_ipsum.words(5, False)

    @factory.lazy_attribute
    def color(self):
        return '#333333'

    @factory.lazy_attribute
    def lab(self):
        return Lab.objects.order_by('?')[0]