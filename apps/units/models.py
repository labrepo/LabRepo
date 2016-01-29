# -*- coding: utf-8 -*-
import os
import urlparse
from urllib import urlencode

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _, ugettext
from django.db.models import signals

from labs.models import Lab
from experiments.models import Experiment
from tags.models import Tag


class Unit(models.Model):
    """
    The model is for storing Unit data. Bind to laboratory

    :lab: reference on laboratory
    :type lab: :class:`labs.documents.Lab`
    :experiments: reference on experiments
    :type experiments: :class:`experiments.documents.Experiment`
    :parent: reference on itself. Need for define SubUnit
    :measurement: reference to model :class:`measurements.documents.Measurement`
    :tags: reference to model :class:`tags.documents.tags`
    """
    lab = models.ForeignKey(Lab, verbose_name=_('lab'))
    experiments = models.ManyToManyField(Experiment, verbose_name=_('experiments'))
    parent = models.ManyToManyField('self', symmetrical=False, blank=True, null=True, related_name='children', db_index=True)
    sample = models.CharField(max_length=4096, verbose_name=_('sample'))
    tags = models.ManyToManyField(Tag, blank=True, null=True, verbose_name=_('tags'))
    active = models.BooleanField(default=True, verbose_name=_('active'))
    description = models.TextField(null=True, blank=True, verbose_name=_('description'))

    # meta = {'create_revision_after_save': True, 'versioned': True, 'related_fkey_lookups': [], 'local_fields': [],
    #         'virtual_fields': [], 'auto_created': False, 'verbose_name': ugettext('unit'), 'verbose_name_plural': ugettext('units')}

    class Meta:
        verbose_name = _('unit')
        verbose_name_plural = _('units')

    def __unicode__(self):
        return u"{}".format(self.sample)

    def get_absolute_url(self):
        return reverse('units:detail', kwargs={'pk': self.pk, 'lab_pk': self.lab.pk})

    def is_owner(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a owner
        :rtype: bool
        """
        for experiment in self.experiments.all():
            if experiment.is_owner(user) or experiment.is_editor(user):
                return True
        return self.lab.is_owner(user)

    def is_member(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a lab's member
        :rtype: bool
        """
        return self.lab.is_member(user)

    def is_viewer(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a viewer
        :rtype: bool
        """
        for experiment in self.experiments.all():
            if experiment.is_viewer(user):
                return True
        # from unit_collections.documents import Collection
        # for collection in Collection.objects.filter(units__in=[self]):
        #     if collection.is_owner(user) or collection.is_editor(user) and user in collection.viewers:
        #         return True
        return self.lab.is_owner(user)  # or self.lab.is_member(user)

    def is_assistant(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a assistant of laboratory
        :rtype: bool
        """
        return self.is_owner(user) or self.is_viewer(user) or self.is_member(user)

    @property
    def links(self):
        return UnitLink.objects.filter(parent=self)

    def get_parent_string(self):
        return ', '.join([x.sample for x in self.parent.all()])


def create_measurement(sender, instance, created, **kwargs):
    """Create Measurement for every new Unit."""
    from measurements.models import Measurement
    if created:
        Measurement.objects.create(unit=instance)

signals.post_save.connect(create_measurement, sender=Unit)


class UnitFile(models.Model):  # todo upd docs
    """
    Base class for file storage in GridFS

    :parent: reference on parent document. Must be overridden
    :file: reference on GridFsProxy object.
    :name: (string) name of the file
    :size: (int) size of file, bytes
    :content_type: (string) file content type, ex 'image/jpeg'
    :thumbnail: reference on GridFsProxy object with file thumbnail, if file is image.
    :outer_thumbnail_url: (string) store outer url to thumbnail for dropbox or gdrive object
    :outer_url: (string) store outer url for dropbox or gdrive object
    :timestamp: (datetime) when object is created
    """
    parent = models.ForeignKey(Unit, verbose_name=_('unit'))
    file = models.FileField(upload_to='unit_files')
    content_type = models.CharField(max_length=256, null=True, blank=True)
    outer_url = models.URLField()
    thumbnail = models.FileField(upload_to='unit_thumbs')
    outer_thumbnail_url = models.URLField()
    timestamp = models.DateTimeField(auto_now=True)

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    def get_outer_thumb(self, size=256):
        if self.outer_thumbnail_url:
            if self.outer_thumbnail_url.startswith('https://api-content.dropbox.com'):
                parsed_url = urlparse.urlparse(self.outer_thumbnail_url)
                query = urlparse.parse_qs(parsed_url.query)
                query['bounding_box'] = size
                parsed_url = parsed_url._replace(query=urlencode(query, True))
                return parsed_url.geturl()

            return self.outer_thumbnail_url

    def delete(self, using=None):
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        if self.thumbnail:
            if os.path.isfile(self.thumbnail.path):
                os.remove(self.thumbnail.path)
        super(UnitFile, self).delete(using)


class UnitLink(models.Model):
    """
    The model is for storing Unit links

    :parent: reference on unit
    """
    parent = models.ForeignKey(Unit, verbose_name=_('unit'))
    link = models.URLField(verbose_name=_('url'))
    timestamp = models.DateTimeField(auto_now=True)
    image = models.URLField(verbose_name=_('image'), blank=True, null=True)
    title = models.TextField(verbose_name=_('title'), blank=True, null=True)
    canonicalUrl = models.URLField(verbose_name=_('canonicalUrl'), blank=True, null=True)
    description = models.TextField(verbose_name=_('description'), blank=True, null=True)

    @property
    def truncated_title(self):
        if len(self.link) > 50:
            return self.link[:45]+'...' + self.link[-5:]
        return self.link

    def is_assistant(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a assistant of laboratory
        :rtype: bool
        """
        return self.parent.is_owner(user) or self.parent.is_viewer(user) or self.parent.is_member(user)
