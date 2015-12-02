from django.utils.translation import ugettext_lazy as _, ugettext
from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models


class LabUser(AbstractUser):
    """Extend Mongo Engine User model"""
    plot_un = models.CharField(max_length=512, blank=True, null=True, verbose_name=_('Plot.ly username(un)'))
    plot_key = models.CharField(max_length=512, blank=True, null=True, verbose_name=_('Plot.ly key'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # avatar = models.ImageField(upload_to='avatars',
    #                            blank=False, null=True,
    #                            # size=None,
    #                            # thumbnail_size=(200, 200, True),
    #                            # collection_name='avatars',
    #                            verbose_name=_('Avatar'))

    def get_username(self):
        return self.email.split('@')[0]

    def full_name(self):
        return self.first_name + ' ' + self.last_name

    class Meta:
        unique_together = ('email', )


class TempPassword(models.Model):
    user = models.ForeignKey(LabUser)
    password = models.TextField()

    def __unicode__(self):
        return self.user.username


