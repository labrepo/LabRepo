# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _, ugettext

from labs.models import Lab
from comments.models import Comment


class Experiment(models.Model):
    """
    The model is for storing Laboratory data.
    To have any role in an experiment, user should belong to the lab this experiment belongs to
    (at least on Guest privileges).

    :lab: reference on laboratory
    :type lab: :class:`labs.documents.Lab`
    :owners: super users for this experiments
    :editors: can edit data, cans delete or edit info of the experiment.
    :viewers: can only browse data. can't edit
    :status: list of values - `Planned`, `In Progress`, `Completed`
    """

    PLANNED, IN_PROGRESS, COMPLETED = range(1, 4)
    STATUS = (
        (PLANNED, _("Planned")),
        (IN_PROGRESS, _("In Progress")),
        (COMPLETED, _("Completed"))
    )

    lab = models.ForeignKey(Lab, verbose_name=_('lab'))
    title = models.CharField(max_length=255, verbose_name=_('title'))
    owners = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='experiments_owner', verbose_name=_('owners'))
    editors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='experiments_editors', blank=True, verbose_name=_('editors'))
    viewers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='experiments_viewers', blank=True, verbose_name=_('viewers'))
    start = models.DateTimeField(verbose_name=_('start'))
    end = models.DateTimeField(verbose_name=_('end'))
    description = models.TextField(blank=True, null=True, verbose_name=_('description'))
    status = models.IntegerField(choices=STATUS, blank=True, null=True, verbose_name=_('status'))
    active = models.BooleanField(default=True, verbose_name=_('active'))
    wooflo_key = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('wooflo project key'))

    class Meta:
        verbose_name = _('experiment')
        verbose_name_plural = _('experiments')

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('experiments:detail', kwargs={'lab_pk': self.lab.pk, 'pk': self.pk})

    def is_owner(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a owner and can delete experiment
        :rtype: bool
        """
        return user in self.owners.all() or self.lab.is_owner(user)

    def is_editor(self, user):
        """
        :param user: User instance
        :return: Checks whether the user can edit experiment
        :rtype: bool
        """
        return self.lab.is_editor(user) or self.is_owner(user)

    def is_viewer(self, user):
        """
        :param user: User instance
        :return: Checks whether the user can view experiment
        :rtype: bool
        """
        return user in self.viewers.all() or self.is_editor(user) or self.is_owner(user)


class ExperimentReadCommentEntry(models.Model):
    """
    Stores information about experiment comment read status for every user
    """
    experiment = models.ForeignKey(Experiment)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='experiments_read')
    comment = models.ForeignKey(Comment, null=True, blank=True)