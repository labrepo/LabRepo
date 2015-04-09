# -*- coding: utf-8 -*-
import json
from mongoengine import Document


class JsonDocumentEncoder(json.JSONEncoder):

    def __init__(self, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, sort_keys=False,
                 indent=None, separators=None, encoding='utf-8', default=None, fields=(), extra_fields=()):
        super(JsonDocumentEncoder, self).__init__(skipkeys, ensure_ascii, check_circular, allow_nan, sort_keys, indent,
                                                  separators, encoding, default)
        self.fields = fields
        self.extra_fields = extra_fields

    def encode_object(self, values):
        row = []
        if not isinstance(values, dict):
            values = dict(zip(self.fields, values))
        for field in list(self.fields) + list(self.extra_fields):
            if not '_pk' in field:
                value = values.get(field)
                if isinstance(value, (list, tuple)):
                    # todo change it
                    arr = [{'text': v.__unicode__(), 'color': v.color or '#ffffff'} if hasattr(v, 'color') else v.__unicode__() for v in value if v and hasattr(v, '__unicode__')]
                    row.append(arr)
                elif isinstance(value, unicode):
                    row.append(value)
                else:
                    if hasattr(value, '__unicode__'):
                        row.append(value.__unicode__())
                    else:
                        row.append(unicode(value or ''))
            else:
                value = values.get(field[:-3])
                if isinstance(value, (list, tuple)):
                    arr = [unicode(v.id) for v in value]
                    row.append(arr)
                elif value and hasattr(value, 'id'):
                    row.append(unicode(value.id))
                else:
                    row.append(value)
        return row

    def default(self, obj):
        if hasattr(obj, '__iter__') and not isinstance(obj, Document):
            return [self.encode_object(x) for x in obj]
        elif isinstance(obj, Document):
            data = obj._data
            data['pk'] = data['id']
            return self.encode_object(data)
        else:
            return self.encode_object(obj)
