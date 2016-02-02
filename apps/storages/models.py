# -*- coding: utf-8 -*-
from django.db import models
from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _, ugettext

from labs.models import Lab


SFTP, S3 = range(1, 3)


class LabStorage(models.Model):
    """
    Filesystem storage for laboratories
    """

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
    public_key = models.TextField(blank=True, null=True, verbose_name=_('SSH key'))
    key_file_name = models.TextField(blank=True, null=True, verbose_name=_('SSH key file name'))
    active = models.BooleanField(default=True, verbose_name=_('Storage status'))

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

    def save(self, *args, **kwargs):
        """
        Set active to True if instance changed
        """
        if self.pk is not None:
            orig = LabStorage.objects.get(pk=self.pk)

            orig_dict = model_to_dict(orig, fields=[field.name for field in
                             self._meta.fields])
            new_dict = model_to_dict(self, fields=[field.name for field in
                             self._meta.fields])

            if self.active != orig.active:
                pass
            elif not self.active and orig_dict != new_dict:
                self.active = True
        super(LabStorage, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'{}: {}@{}{}'.format(self.get_type_display(), self.username, self.host, self.get_path())
