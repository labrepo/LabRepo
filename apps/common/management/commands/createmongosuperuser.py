"""
Management utility to create superusers.
"""
from __future__ import unicode_literals
from django.contrib.auth.hashers import make_password

from django.core.management.base import BaseCommand
from mongoengine.django.auth import User


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.UserModel = User
        self.username_field = 'username'

    help = 'Used to create a superuser.'

    def handle(self, *args, **options):
        username = "admin"
        user_data = {
            self.UserModel.USERNAME_FIELD: username,
            'password': 'admin',
            'email': 'admin@example.com'
        }
        new_user, created = self.UserModel.objects.get_or_create(email=user_data['email'], defaults=user_data)
        new_user.password = make_password(user_data['password'])
        new_user.is_superuser = True
        new_user.is_staff = True
        new_user.is_active = True
        new_user.save()

        self.stdout.write("Superuser created successfully.")
