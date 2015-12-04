# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import gettext_lazy as _, ugettext


class Lab(models.Model):
    """
    Science laboratories

    :name: Title of science laboratory.
    :investigator: Principal Investigator (PI) is a super user. Can view/edit everything that belong to a Lab.
    :members: Members are the ordinary users. By default can only see the list of experiments.
    :guests: Guests can not see the list of experiments (only those experiments they are added to).
    """
    name = models.CharField(verbose_name=_('name'), max_length=255)
    investigator = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='labs_investigator', verbose_name=_('investigators'))
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='labs_members', verbose_name=_('members'), blank=True)
    guests = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='labs_guests', blank=True, verbose_name=_('guests'))
    is_test = models.BooleanField(default=False, verbose_name=_('test lab'))
    # storages = models.ListField(models.ReferenceField(LabStorage), verbose_name=_('storages'))

    # meta = {'related_fkey_lookups': [], 'virtual_fields': [], 'verbose_name': ugettext('lab'), 'verbose_name_plural': ugettext('labs')}

    class Meta:
        verbose_name = _('lab')
        verbose_name_plural = _('labs')

    def __unicode__(self):
        return u'{}'.format(self.name)

    def get_absolute_url(self):
        return reverse('labs:detail', kwargs={'lab_pk': self.pk})

    def is_guest(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a guest
        :rtype: bool
        """
        return user in self.guests.all()

    def is_member(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a member
        :rtype: bool
        """
        return user in self.members.all()

    def is_owner(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a principal investigator
        :rtype: bool
        """
        return user in self.investigator.all()

    def is_assistant(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a assistant of laboratory
        :rtype: bool
        """
        return self.is_guest(user) or self.is_member(user) or self.is_owner(user)


class LabStorage(models.Model):
    """
    Filesystem storage for laboratories
    """

    FS_TYPES = (
        ('SFTP', 'SFTP'),
        ('s3', 's3'),
    )
    lab = models.ForeignKey(Lab, related_name='storages', verbose_name=_('lab'))
    type = models.CharField(verbose_name=_('type'), choices=FS_TYPES, max_length=255)
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
        if self.type == 'SFTP':
            return u'SFTP: {}@{}{}'.format(self.username, self.host, self.get_path())
        return u'{}'.format(self.name)
