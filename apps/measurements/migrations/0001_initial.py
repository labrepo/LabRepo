# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Measurement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('table_data', jsonfield.fields.JSONField(default=[[b'', b'']], verbose_name='table data')),
                ('headers', jsonfield.fields.JSONField(default=[b'', b''], verbose_name='headers')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('unit', models.OneToOneField(to='units.Unit')),
            ],
        ),
    ]
