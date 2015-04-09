import factory

from django.contrib.webdesign import lorem_ipsum

from mongoengine.django.auth import User

from .documents import Comment
from experiments.documents import Experiment
from labs.documents import Lab


class CommentFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Comment

    @factory.lazy_attribute
    def lab(self):
        return Lab.objects.order_by('?')[0]

    @factory.lazy_attribute
    def init_user(self):
        return User.objects.order_by('?')[0]

    @factory.lazy_attribute
    def text(self):
        return lorem_ipsum.words(5, False)

    @factory.lazy_attribute
    def instance_type(self):
        return 'Experiment'

    @factory.lazy_attribute
    def object_id(self):
        return Experiment.objects.order_by('?')[0]
