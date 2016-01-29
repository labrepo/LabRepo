"""
Management utility to create test user.
"""
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from profiles.models import LabUser


class Command(BaseCommand):

    help = 'Used to create a test user.'

    def handle(self, *args, **options):
        if not LabUser.objects.filter(email='demo@demo.demo'):
            user = LabUser.objects.create(
                email='demo@demo.demo',
                username='demo@demo.demo',
                first_name='demo',
                last_name='demo',
                password='demo'
            )
            user.set_password('demo')
            user.is_active = True
            user.save()
            self.stdout.write("Test user created successfully.")
            return
        else:
            self.stdout.write("Test user already created.")