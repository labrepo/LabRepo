# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('labs', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='labstorage',
            name='lab',
        ),
        migrations.DeleteModel(
            name='LabStorage',
        ),
    ]
