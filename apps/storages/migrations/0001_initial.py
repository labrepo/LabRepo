# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('labs', '0002_auto_20151223_2206'),
    ]

    operations = [
        migrations.CreateModel(
            name='LabStorage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.IntegerField(verbose_name='type', choices=[(1, 'SFTP'), (2, 'S3')])),
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
