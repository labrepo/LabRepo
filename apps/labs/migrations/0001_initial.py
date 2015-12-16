# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Lab',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('is_test', models.BooleanField(default=False, verbose_name='test lab')),
                ('guests', models.ManyToManyField(related_name='labs_guests', verbose_name='guests', to=settings.AUTH_USER_MODEL, blank=True)),
                ('investigator', models.ManyToManyField(related_name='labs_investigator', verbose_name='investigators', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(related_name='labs_members', verbose_name='members', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'verbose_name': 'lab',
                'verbose_name_plural': 'labs',
            },
        ),
        migrations.CreateModel(
            name='LabStorage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=255, verbose_name='type', choices=[(b'SFTP', b'SFTP'), (b's3', b's3')])),
                ('readonly', models.BooleanField(default=False, verbose_name='read only')),
                ('username', models.CharField(max_length=255, verbose_name='username')),
                ('host', models.CharField(max_length=255, verbose_name='host')),
                ('path', models.CharField(max_length=512, null=True, verbose_name='path', blank=True)),
                ('folder_name', models.CharField(max_length=255, null=True, verbose_name='folder name', blank=True)),
                ('password', models.CharField(max_length=255, null=True, verbose_name='password', blank=True)),
                ('port', models.PositiveIntegerField(null=True, verbose_name='port', blank=True)),
                ('key_file', models.FileField(upload_to=b'ssh_keys', null=True, verbose_name='SSH key file', blank=True)),
                ('lab', models.ForeignKey(related_name='storages', verbose_name='lab', to='labs.Lab')),
            ],
        ),
    ]
