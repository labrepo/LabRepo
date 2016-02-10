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

    class Meta:
        verbose_name = _('lab')
        verbose_name_plural = _('labs')

    def __unicode__(self):
        return u'{}'.format(self.name)

    def get_absolute_url(self):
        return reverse('labs:detail', kwargs={'lab_pk': self.pk})

    def is_owner(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a principal investigator and can delete lab.
        :rtype: bool
        """
        return user in self.investigator.all()

    def is_editor(self, user):
        """
        :param user: User instance
        :return: Checks whether the user can edit
        :rtype: bool
        """
        return user in self.members.all() or self.is_owner(user)

    def is_viewer(self, user):
        """
        :param user: User instance
        :return: Checks whether the user can view lab
        :rtype: bool
        """
        return user in self.guests.all() or self.is_editor(user) or self.is_owner(user)