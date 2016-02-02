# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storages', '0003_auto_20160125_2147'),
    ]

    operations = [
        migrations.AddField(
            model_name='labstorage',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Storage status'),
        ),
    ]
