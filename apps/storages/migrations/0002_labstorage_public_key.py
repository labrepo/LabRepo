# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='labstorage',
            name='public_key',
            field=models.TextField(null=True, verbose_name='SSH key', blank=True),
        ),
    ]
