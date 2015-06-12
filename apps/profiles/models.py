from django.utils.translation import ugettext_lazy as _, ugettext
from mongoengine.django.auth import User

import mongoengine as me


class LabUser(User):
    """Extend Mongo Engine User model"""
    plot_un = me.StringField(required=False, verbose_name=_('Plot.ly username(un)'))
    plot_key = me.StringField(required=False, verbose_name=_('Plot.ly key'))

LabUser._default_manager = LabUser.objects
User._default_manager = User.objects
