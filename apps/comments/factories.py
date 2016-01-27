import factory

from django.utils import lorem_ipsum

from profiles.models import LabUser
from experiments.factories import ExperimentFactory
from .models import Comment


class CommentFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Comment

    @factory.lazy_attribute
    def init_user(self):
        return LabUser.objects.order_by('?')[0]

    @factory.lazy_attribute
    def text(self):
        return lorem_ipsum.words(5, False)

    content_object = factory.SubFactory(ExperimentFactory)

