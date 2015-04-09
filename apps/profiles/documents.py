import mongoengine as me
from mongoengine.django.auth import User


class TempPassword(me.Document):
    user = me.ReferenceField(User)
    password = me.StringField()

    def __unicode__(self):
        return self.user.username

TempPassword._default_manager = TempPassword.objects
