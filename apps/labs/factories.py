import factory

from django.utils import lorem_ipsum

from labs.models import Lab


class LabFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Lab

    @factory.lazy_attribute
    def name(self):
        return lorem_ipsum.words(5, False)

    @factory.post_generation
    def investigator(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for user in extracted:
                self.investigator.add(user)

    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for user in extracted:
                self.members.add(user)

    @factory.post_generation
    def guests(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for user in extracted:
                self.guests.add(user)