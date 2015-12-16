# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '__first__'),
        ('tags', '__first__'),
        ('labs', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sample', models.CharField(max_length=4096, verbose_name='sample')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('experiments', models.ManyToManyField(to='experiments.Experiment', verbose_name='experiments')),
                ('lab', models.ForeignKey(verbose_name='lab', to='labs.Lab')),
                ('parent', models.ManyToManyField(db_index=True, related_name='children', null=True, to='units.Unit', blank=True)),
                ('tags', models.ManyToManyField(to='tags.Tag', null=True, verbose_name='tags', blank=True)),
            ],
            options={
                'verbose_name': 'unit',
                'verbose_name_plural': 'units',
            },
        ),
        migrations.CreateModel(
            name='UnitFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=b'unit_files')),
                ('content_type', models.CharField(max_length=256, null=True, blank=True)),
                ('outer_url', models.URLField()),
                ('thumbnail', models.FileField(upload_to=b'unit_thumbs')),
                ('outer_thumbnail_url', models.URLField()),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(verbose_name='unit', to='units.Unit')),
            ],
        ),
        migrations.CreateModel(
            name='UnitLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('link', models.URLField(verbose_name='url')),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('image', models.URLField(null=True, verbose_name='image', blank=True)),
                ('title', models.TextField(null=True, verbose_name='title', blank=True)),
                ('canonicalUrl', models.URLField(null=True, verbose_name='canonicalUrl', blank=True)),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('parent', models.ForeignKey(verbose_name='unit', to='units.Unit')),
            ],
        ),
    ]
