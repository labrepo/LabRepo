from django.utils.translation import ugettext_lazy as _, ugettext
from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.hashers import is_password_usable

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


class LabUser(AbstractUser):
    """Extend Mongo Engine User model"""
    plot_un = models.CharField(max_length=512, blank=True, null=True, verbose_name=_('Plot.ly username(un)'))
    plot_key = models.CharField(max_length=512, blank=True, null=True, verbose_name=_('Plot.ly key'))

    avatar = models.ImageField(upload_to='avatars',
                               blank=True, null=True,
                               verbose_name=_('Avatar'))

    avatar_thumbnail = ImageSpecField(source='avatar',
                                      processors=[ResizeToFill(80, 80)],
                                      format='JPEG',
                                      options={})

    def get_username(self):
        if self.first_name or self.last_name:
            return ' '.join([self.first_name, self.last_name])
        if self.email:
            return self.email.split('@')[0]

    @property
    def full_name(self):
        if self.first_name or self.last_name:
            return self.first_name + ' ' + self.last_name
        return self.get_username()

    def has_usable_password(self):
        return is_password_usable(self.password)

    def get_absolute_url(self):
        return reverse('profiles:detail', kwargs={'pk': self.pk})

    class Meta:
        unique_together = ('email', )


class TempPassword(models.Model):
    user = models.ForeignKey(LabUser)
    password = models.TextField()

    def __unicode__(self):
        return self.user.username


