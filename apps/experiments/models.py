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
        :return: Checks whether the user is a owner
        :rtype: bool
        """
        return user in self.owners.all() or self.lab.is_owner(user)

    def is_member(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a lab's member
        :rtype: bool
        """
        return self.lab.is_member(user)

    def is_editor(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a editor
        :rtype: bool
        """
        return user in self.editors.all()

    def is_viewer(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a viewer
        :rtype: bool
        """
        return user in self.viewers.all()

    def is_experiment_assistant(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a assistant of experiment
        :rtype: bool
        """
        return self.is_owner(user) or self.is_editor(user) or self.is_viewer(user)

    def is_assistant(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a assistant of laboratory
        :rtype: bool
        """
        return self.is_experiment_assistant(user) or self.is_member(user)


class ExperimentReadCommentEntry(models.Model):
    """
    Stores information about experiment comment read status for every user
    """
    experiment = models.ForeignKey(Experiment)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='experiments_read')
    comment = models.ForeignKey(Comment, null=True, blank=True)