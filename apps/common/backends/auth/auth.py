from django.contrib import auth

from mongoengine.django.auth import MongoEngineBackend


class MongoEngineEmailBackend(MongoEngineBackend):

    def authenticate(self, username=None, password=None):
        user = self.user_document.objects(email=username).first()
        if user:
            if password and user.check_password(password):
                backend = auth.get_backends()[0]
                user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
                return user
        return None
