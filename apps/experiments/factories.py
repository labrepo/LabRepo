import datetime
import random
import factory

from django.contrib.webdesign import lorem_ipsum

from experiments.models import Experiment
from labs.models import Lab


class ExperimentFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Experiment

    @factory.lazy_attribute
    def lab(self):
        return Lab.objects.order_by('?')[0]

    @factory.lazy_attribute
    def start(self):
        return datetime.datetime.now()

    @factory.lazy_attribute
    def end(self):
        return datetime.datetime.now()

    @factory.lazy_attribute
    def description(self):
        return lorem_ipsum.words(5, False)

    @factory.lazy_attribute
    def title(self):
        return lorem_ipsum.words(5, False)

    @factory.lazy_attribute
    def status(self):
        return Experiment.STATUS[random.randint(0, 2)][0]

    @factory.post_generation
    def owners(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for user in extracted:
                self.owners.add(user)

    @factory.post_generation
    def editors(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for user in extracted:
                self.editors.add(user)

    @factory.post_generation
    def viewers(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for user in extracted:
                self.viewers.add(user)