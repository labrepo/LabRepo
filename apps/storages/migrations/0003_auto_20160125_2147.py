# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storages', '0002_labstorage_public_key'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='labstorage',
            name='key_file',
        ),
        migrations.AddField(
            model_name='labstorage',
            name='key_file_name',
            field=models.TextField(null=True, verbose_name='SSH key file name', blank=True),
        ),
    ]
