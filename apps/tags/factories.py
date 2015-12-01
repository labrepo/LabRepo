import json
import factory

from django.contrib.webdesign import lorem_ipsum

from .models import Tag
from labs.models import Lab


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