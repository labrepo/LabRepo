# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('action_time', models.DateTimeField(auto_now=True)),
                ('text', models.TextField()),
                ('init_user', models.ForeignKey(related_name='user', to=settings.AUTH_USER_MODEL)),
                ('instance_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['-action_time'],
                'verbose_name': 'comment',
                'verbose_name_plural': 'comments',
            },
        ),
    ]
