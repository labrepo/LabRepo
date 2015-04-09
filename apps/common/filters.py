# -*- coding: utf-8 -*-

from django.contrib import admin
import mongoengine as me


class MongoRelatedFieldListFilter(admin.filters.RelatedFieldListFilter):
    template = 'admin/filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        super(MongoRelatedFieldListFilter, self).__init__(field, request, params, model, model_admin, field_path)
        self.lookup_kwarg = '%s__exact' % field_path


admin.filters.FieldListFilter.register(
    lambda f: isinstance(f, me.ReferenceField), MongoRelatedFieldListFilter)
