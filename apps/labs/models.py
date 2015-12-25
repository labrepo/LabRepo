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
