from datetime import datetime
from bson import DBRef

from mongoengine import Document, Q, DoesNotExist
from mongoengine.base.common import get_document
from mongoengine.django.auth import User
from mongoengine.fields import DictField, StringField, ReferenceField, DateTimeField, ListField, ObjectIdField, EmbeddedDocumentField
from mongoreversion.models import ReversionedDocument, ContentType, Revision
from experiments.documents import Experiment
from labs.documents import Lab


class HistoryDocument(ReversionedDocument):
    """
    Abstract class for add revision system for other class
    """
    meta = {'abstract': True}

    @property
    def revisions(self):
        """
        Get all object's revision

        :return: All revision of object
        """
        instance_type = ContentType.objects.get(class_name=self._class_name)
        return History.objects.filter(instance_type=instance_type, instance_id=self.pk).order_by('-timestamp')

    def save_revision(self, user, comment=''):
        """
        Save revision.

        :param user: User by whom was created or changed unit or measurement.
        :param comment: Text why the object was created or changed.
        :return: revision instance
        """
        return History.save_revision(user, self, comment)

    def save(self, *args, **kwargs):
        """
        Check if user in kwargs otherwise raise error 'user must be passed to instance save when
        create_revision_after_save=True'

        :return: revision instance
        """
        user = kwargs.pop('user', None) or self._data.pop('user', None) or self._meta._meta.get('_data', {}).get('user')
        r = super(ReversionedDocument, self).save(*args, **kwargs)
        if self._meta.get('create_revision_after_save', False):
            if not user:
                raise ValueError('user must be passed to instance save when create_revision_after_save=True')
            self.save_revision(user, kwargs.get('revision_comment', ''))
        return r


class History(Document):
    """
    Revision system

    :user: User by whom was created or changed unit or measurement.
    :timestamp: Timestamp when object was created or changed.
    :instance_data: Object's copy.
    :instance_related_revisions: Link for revision related objects.
    :instance_type: Type of object.
    :instance_id: Object's ID.
    :comment: Text why the object was created or changed.
    """
    user = ReferenceField(User, dbref=False, required=True)
    timestamp = DateTimeField(default=datetime.now, required=True)
    instance_data = DictField()
    instance_related_revisions = DictField()
    instance_type = ReferenceField(ContentType, dbref=False, required=True)
    instance_id = ObjectIdField(required=True)
    comment = StringField(required=False)

    def __unicode__(self):
        return 'Revision user=%s, time=%s' % (self.user, self.timestamp.strftime('%d/%m/%Y %H:%M'))

    @property
    def get_object(self):
        """
        :return: instance of object by his :instance type: and ID
        """
        try:
            return get_document(self.instance_type.class_name).objects.get(pk=self.instance_id)
        except DoesNotExist:
            return None

    def is_assistant(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a assistant
        :rtype: bool
        """
        labs = Lab.objects.filter(Q(investigator=user.id), Q(members=user.id), Q(guests=user.id))
        experiments = Experiment.objects.filter(Q(owners=user.id), Q(editors=user.id), Q(viewers=user.id))
        return labs or experiments

    def is_owner(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a owner
        :rtype: bool
        """
        return self.is_assistant(user)

    def is_member(self, user):
        """
        :param user: User instance
        :return: Checks whether the user is a lab's member
        :rtype: bool
        """
        return self.is_assistant(user)

    @classmethod
    def save_revision(cls, user, instance, comment=None):
        """
        Save revision
        :param user: User by whom was created or changed unit or measurement.
        :param instance: Object's instance
        :param comment: Text why the object was created or changed.
        :return: Revision instance
        """
        if not instance._meta.get('versioned', None):
            raise ValueError('instance meta does not specify it to be versioned, set versioned=True to enable')

        instance_type, is_new = ContentType.objects.get_or_create(class_name=instance._class_name)
        instance_data = dict(instance._data)
        instance_related_revisions = {}

        # ensure instance has been saved at least once
        if not instance.pk:
            instance.save()

        # Save instance ID in data dict
        instance_data['id'] = instance.pk

        # Remove None entry if it exists
        if None in instance_data:
            del instance_data[None]

        # create lookup of related field types
        related_field_types = {}
        for key, field in instance._fields.items():
            related_field_type = None
            if isinstance(field, ListField):
                if isinstance(field.field, (ReferenceField, EmbeddedDocumentField)):
                    related_field_type = field.field.document_type_obj
            elif isinstance(field, ReferenceField):
                related_field_type = field.document_type_obj
            # TODO: elif isinstance(field, DictField):

            if related_field_type:
                related_field_types[key] = related_field_type

        # process field data
        for key, value in instance_data.items():

            if key in related_field_types:
                # check if related field is versioned, store revision data
                if hasattr(related_field_types.get(key), '_meta') and related_field_types.get(key)._meta.get('versioned', None):

                    # versioned, store revision ID(s)
                    if isinstance(value, (list, tuple)):
                        id_revisions = []
                        for v in value:
                            revision = cls.latest_revision(v)
                            # TODO: if latest revision doesn't exist then maybe
                            # it should be created here
                            if revision:
                                id_revisions.append(revision.pk)
                            else:
                                # if no revision exists, then explicitely
                                # store a None entry
                                id_revisions.append(None)
                            instance_related_revisions[key] = id_revisions
                    else:
                        revision = cls.latest_revision(value)
                        # TODO: if latest revision doesn't exist then maybe it
                        # should be created here
                        if revision:
                            instance_related_revisions[key] = revision.pk
                        else:
                            # if no revision exists, then explicitely store a
                            # None entry
                            instance_related_revisions[key] = None

                # store object ID(s) in instance_data
                if isinstance(value, (list, tuple)):
                    instance_data[key] = [v for v in value]
                else:
                    instance_data[key] = value

            else:
                # store data as is
                instance_data[key] = value

        # create the revision, but do not save it yet
        revision = cls(user=user, timestamp=datetime.now(), instance_type=instance_type, instance_data=instance_data,
                       instance_related_revisions=instance_related_revisions, instance_id=instance.pk, comment=comment)

        # check for any differences in data from lastest revision
        # return the latest revision if no difference
        latest_revision = cls.latest_revision(instance)
        if latest_revision:
            diff = revision.diff(latest_revision)
            if not diff:
                return latest_revision, False

        # save revision and return
        revision.save()
        return revision, True

    @classmethod
    def latest_revision(cls, instance):
        """
        :param instance: Object's instance.
        :return: Object's latest revision.
        """
        try:
            if not isinstance(instance, DBRef):
                instance_type = ContentType.objects.get(class_name=instance._class_name)
                revisions = cls.objects.filter(instance_type=instance_type, instance_id=instance.pk).order_by('-timestamp')
                if revisions.count() > 0:
                    return revisions[0]
        except ContentType.DoesNotExist:
            pass
        return None

    @property
    def instance(self):
        instance_model = self.instance_type.document_model()
        data = dict(self.instance_data)
        for key, value in data.items():
            if key in self.related_field_types:
                if key in self.instance_related_revisions:
                    revision_value = self.instance_related_revisions.get(key)
                    if isinstance(revision_value, (list, tuple)):
                        values = []
                        for i, rev_id in enumerate(revision_value):
                            if rev_id:
                                revision = self.__class__.objects.get(pk=rev_id)
                                values.append(revision.instance)
                            else:
                                obj_id = value[i]
                                values.append(self.related_field_types.get(key).objects.get(pk=obj_id))
                        data[key] = values
                    else:
                        if value:
                            revision = self.__class__.objects.get(pk=value.pk)
                            data[key] = revision.instance
                        else:
                            data[key] = self.related_field_types.get(key).objects.get(pk=value.pk)
                else:
                    if isinstance(value, (list, tuple)):
                        data[key] = [self.related_field_types.get(key).objects.get(pk=v.pk) for v in value]
                    else:
                        data[key] = self.related_field_types.get(key).objects.get(pk=value.pk)
        return instance_model(**data)

    def diff(self, revision=None):
        """
        Returns the diff of the current revision with the given revision.
        If the given revision is empty, use the latest revision of the
        document instance.
        """
        if not revision:
            revision = self.__class__.latest_revision(self.instance)
        if not revision:
            return self.instance_data
        diff_dict = {}
        for key, value in self.instance_data.items():
            if isinstance(value, datetime):
                if value != revision.instance_data.get(key): #value.replace(tzinfo=None)
                    diff_dict[key] = value
            else:
                if value != revision.instance_data.get(key):
                    diff_dict[key] = value
        return diff_dict


History.revert = staticmethod(Revision.revert)
History._default_manager = History.objects
