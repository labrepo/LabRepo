# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext_lazy as _, ugettext

from labs.models import Lab


class LabStorage(models.Model):
    """
    Filesystem storage for laboratories
    """
    SFTP, S3 = range(1, 3)
    FS_TYPES = [
        (SFTP, ugettext("SFTP")),
        (S3, ugettext("S3")),
    ]

    lab = models.ForeignKey(Lab, related_name='storages', verbose_name=_('lab'))
    type = models.IntegerField(verbose_name=_('type'), choices=FS_TYPES)
    readonly = models.BooleanField(verbose_name=_('read only'), default=False)
    username = models.CharField(verbose_name=_('username'), max_length=255)
    host = models.CharField(verbose_name=_('host'), max_length=255)
    path = models.CharField(verbose_name=_('path'), max_length=512, blank=True, null=True)
    folder_name = models.CharField(verbose_name=_('folder name'), max_length=255,  blank=True, null=True)
    password = models.CharField(verbose_name=_('password'), max_length=255,  blank=True, null=True)
    port = models.PositiveIntegerField(verbose_name=_('port'), blank=True, null=True)
    key_file = models.FileField(upload_to='ssh_keys', blank=True, null=True, verbose_name=_('SSH key file'))

    def get_path(self):
        if self.path:
            return self.path
        else:
            return u'/home/{}/'.format(self.username)

    def get_folder_name(self):
        if self.folder_name:
            return self.folder_name
        fs_name = u'{}@{}'.format(self.username, self.host)
        if self.readonly:
            fs_name += u'(readonly)'
        return fs_name

    def __unicode__(self):
        return u'{}: {}@{}{}'.format(self.get_type_display(), self.username, self.host, self.get_path())
