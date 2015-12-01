from datetime import datetime
from bson import DBRef
from django.db import models
# from mongoengine import Document, Q, DoesNotExist
# from mongoengine.base.common import get_document
# from mongoengine.django.auth import User
# from mongoengine.fields import DictField, StringField, ReferenceField, DateTimeField, ListField, ObjectIdField, EmbeddedDocumentField
# from mongoreversion.models import ReversionedDocument, ContentType, Revision
from experiments.models import Experiment
from labs.models import Lab


class HistoryDocument(models.Model):
    """
    Abstract class for add revision system for other class
    """
    # meta = {'abstract': True}
    pass

class History(models.Model):
    """
    Abstract class for add revision system for other class
    """
    # meta = {'abstract': True}
    pass