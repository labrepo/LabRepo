# -*- coding: utf-8 -*-
import urlparse
from datetime import datetime
from urllib import urlencode

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
    :thumbnail: reference on GridFsProxy object with file thumbnail, if file is image.
    :outer_thumbnail_url: (string) store outer url to thumbnail for dropbox or gdrive object
    :outer_url: (string) store outer url for dropbox or gdrive object
    :timestamp: (datetime) when object is created
    """
    # parent = me.ReferenceField('Unit', reverse_delete_rule=CASCADE, required=True, verbose_name=_('unit'))
    file = me.FileField()
    name = me.StringField()
    size = me.IntField()
    content_type = me.StringField()
    outer_url = me.StringField()
    thumbnail = me.FileField()
    outer_thumbnail_url = me.StringField()
    timestamp = me.DateTimeField(default=datetime.now, required=True)
    meta = {'abstract': True}

    def get_outer_thumb(self, size=256):
        if self.outer_thumbnail_url:
            if self.outer_thumbnail_url.startswith('https://api-content.dropbox.com'):
                parsed_url = urlparse.urlparse(self.outer_thumbnail_url)
                query = urlparse.parse_qs(parsed_url.query)
                query['bounding_box'] = size
                parsed_url = parsed_url._replace(query=urlencode(query, True))
                return parsed_url.geturl()

            return self.outer_thumbnail_url

    def delete(self):
        """
        Remove file from GridFS
        """
        self.file.delete()
        super(BaseFile, self).delete()
