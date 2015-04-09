from mongoengine.django.auth import User


User._default_manager = User.objects
