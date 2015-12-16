# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '__first__'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('labs', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecentActivity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField(null=True, blank=True)),
                ('object_id', models.PositiveIntegerField()),
                ('action_flag', models.IntegerField(choices=[(1, 'created'), (2, 'updated'), (3, 'removed'), (4, 'commented')])),
                ('action_time', models.DateTimeField(auto_now=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('experiments', models.ManyToManyField(to='experiments.Experiment', blank=True)),
                ('init_user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('lab_id', models.ForeignKey(to='labs.Lab')),
            ],
            options={
                'ordering': ['-action_time'],
                'verbose_name': 'recent activity',
                'verbose_name_plural': 'recent activities',
            },
        ),
    ]
