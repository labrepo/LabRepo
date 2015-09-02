# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _, ugettext

import mongoengine as me


class BaseFile(me.Document):
    """
    Base class for file storage in GridFS

    :parent: reference on parent document. Must be overridden
    :file: reference on GridFsProxy object.
    :name: (string) name of the file
    :size: (int) size of file, bytes
    :content_type: (string) file content type, ex 'image/jpeg'
    :outer_url: (string) store outer url for dropbox or gdrive object
    """
    # parent = me.ReferenceField('Unit', reverse_delete_rule=CASCADE, required=True, verbose_name=_('unit'))
    file = me.FileField()
    name = me.StringField()
    size = me.IntField()
    content_type = me.StringField()
    outer_url = me.StringField()

    meta = {'abstract': True}

    def delete(self):
        """
        Remove file from GridFS
        """
        self.file.delete()
        super(BaseFile, self).delete()
