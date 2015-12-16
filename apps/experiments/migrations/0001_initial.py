# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('labs', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('start', models.DateTimeField(verbose_name='start')),
                ('end', models.DateTimeField(verbose_name='end')),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('status', models.IntegerField(blank=True, null=True, verbose_name='status', choices=[(1, 'Planned'), (2, 'In Progress'), (3, 'Completed')])),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('wooflo_key', models.CharField(max_length=255, null=True, verbose_name='wooflo project key', blank=True)),
                ('editors', models.ManyToManyField(related_name='experiments_editors', verbose_name='editors', to=settings.AUTH_USER_MODEL, blank=True)),
                ('lab', models.ForeignKey(verbose_name='lab', to='labs.Lab')),
                ('owners', models.ManyToManyField(related_name='experiments_owner', verbose_name='owners', to=settings.AUTH_USER_MODEL)),
                ('viewers', models.ManyToManyField(related_name='experiments_viewers', verbose_name='viewers', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'verbose_name': 'experiment',
                'verbose_name_plural': 'experiments',
            },
        ),
        migrations.CreateModel(
            name='ExperimentReadCommentEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.ForeignKey(blank=True, to='comments.Comment', null=True)),
                ('experiment', models.ForeignKey(to='experiments.Experiment')),
                ('user', models.ForeignKey(related_name='experiments_read', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
