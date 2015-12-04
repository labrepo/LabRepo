from django.contrib import admin

from reversion.admin import VersionAdmin

from .models import Unit


class UnitAdmin(VersionAdmin):
    """
    Register django-revisions for a model
    """
    pass

admin.site.register(Unit, UnitAdmin)


# from functools import partial
#
# from django.contrib.admin.util import flatten_fieldsets, NestedObjects
# from django.core.urlresolvers import reverse
# from django.forms.models import modelform_defines_fields
# from django.forms.formsets import DELETION_FIELD_NAME
# from django.utils.text import get_text_list
# from django.utils.translation import gettext_lazy as _
#
# from mongoadmin import site, EmbeddedTabularDocumentInline
# from mongodbforms import embeddedformset_factory
# from mongoengine import ValidationError
#
# from .documents import Unit
# from measurements.documents import Measurement
# from measurements.forms import MeasurementAdminForm
# from units.forms import MeasurementFormSet
# from common.admin import DocumentAdmin
#
#
# class MeasurementInline(EmbeddedTabularDocumentInline):
#     model = Measurement
#     document = Measurement
#     parent_document = Unit
#     parent_field_name = 'measurements'
#     form = MeasurementAdminForm
#     formset = MeasurementFormSet
#     extra = 1
#
#     def get_queryset(self, request):
#         if request.resolver_match.args:
#             return getattr(self.parent_model._default_manager.get(pk=request.resolver_match.args[0]), self.parent_field_name, [])
#         return self.model.objects.none()
#
#     def get_formset(self, request, obj=None, **kwargs):
#         """Returns a BaseInlineFormSet class for use in admin add/change views."""
#         if 'fields' in kwargs:
#             fields = kwargs.pop('fields')
#         else:
#             fields = flatten_fieldsets(self.get_fieldsets(request, obj))
#         if self.exclude is None:
#             exclude = []
#         else:
#             exclude = list(self.exclude)
#         exclude.extend(self.get_readonly_fields(request, obj))
#         if self.exclude is None and hasattr(self.form, '_meta') and self.form._meta.exclude:
#             # Take the custom ModelForm's Meta.exclude into account only if the
#             # InlineModelAdmin doesn't define its own.
#             exclude.extend(self.form._meta.exclude)
#         # if exclude is an empty list we use None, since that's the actual
#         # default
#         exclude = exclude or None
#         can_delete = self.can_delete and self.has_delete_permission(request, obj)
#         defaults = {
#             "form": self.form,
#             "formset": self.formset,
#             "fields": fields,
#             "exclude": exclude,
#             "formfield_callback": partial(self.formfield_for_dbfield, request=request),
#             "extra": self.get_extra(request, obj, **kwargs),
#             "max_num": self.get_max_num(request, obj, **kwargs),
#             "can_delete": can_delete,
#         }
#
#         defaults.update(kwargs)
#         base_model_form = defaults['form']
#
#         class DeleteProtectedModelForm(base_model_form):
#             def hand_clean_DELETE(self):
#                 """
#                 We don't validate the 'DELETE' field itself because on
#                 templates it's not rendered using the field information, but
#                 just using a generic "deletion_field" of the InlineModelAdmin.
#                 """
#                 if self.cleaned_data.get(DELETION_FIELD_NAME, False):
#                     collector = NestedObjects()
#                     collector.collect([self.instance])
#                     if collector.protected:
#                         objs = []
#                         for p in collector.protected:
#                             objs.append(
#                                 # Translators: Model verbose name and instance representation, suitable to be an item in a list
#                                 _('%(class_name)s %(instance)s') % {
#                                     'class_name': p._meta.verbose_name,
#                                     'instance': p}
#                             )
#                         params = {'class_name': self._meta.model._meta.verbose_name,
#                                   'instance': self.instance,
#                                   'related_objects': get_text_list(objs, _('and'))}
#                         msg = _("Deleting %(class_name)s %(instance)s would require "
#                                 "deleting the following protected related objects: "
#                                 "%(related_objects)s")
#                         raise ValidationError(msg, code='deleting_protected', params=params)
#
#             def is_valid(self):
#                 result = super(DeleteProtectedModelForm, self).is_valid()
#                 self.hand_clean_DELETE()
#                 return result
#
#         defaults['form'] = DeleteProtectedModelForm
#
#         if defaults['fields'] is None and not modelform_defines_fields(defaults['form']):
#             defaults['fields'] = None
#
#         return embeddedformset_factory(self.model, self.parent_model, **defaults)
#
#
# class UnitAdmin(DocumentAdmin):
#     change_form_template = 'admin/admin_change_form.html'
#     list_display = ('sample', 'labs', 'experiment', 'parents') #, 'tags')
#     # list_filter = (('tags', MongoRelatedFieldListFilter), ('lab', MongoRelatedFieldListFilter),
#     #                #('experiments', MongoRelatedFieldListFilter), ('parents', MongoRelatedFieldListFilter),
#     # )
#     inlines = (MeasurementInline,)
#
#     def save_model(self, request, obj, form, change):
#         """
#         Given a model instance save it to the database.
#         """
#         obj.save(user=request.user)
#
#     def save_formset(self, request, form, formset, change):
#         setattr(self.model._meta, '_data', {'user': request.user})
#         for inline in self.inlines:
#             inline.model._meta._meta['_data'] = {'user': request.user}
#         super(UnitAdmin, self).save_formset(request, form, formset, change)
#
#     def experiment(self, inst):
#         return ','.join([u'<a href="{0}">{1}</a>'.format(
#             reverse('admin:experiments_experiment_change', args=[experiment.id]),
#             experiment.__unicode__()) for experiment in inst.experiments])
#
#     experiment.allow_tags = True
#     experiment.short_description = _('experiments')
#
#     def parents(self, inst):
#         return ','.join([u'<a href="{0}">{1}</a>'.format(
#             reverse('admin:units_unit_change', args=[unit.id]),
#             unit.__unicode__()) for unit in inst.parent if hasattr(unit, '__unicode__')])
#
#     parents.allow_tags = True
#     parents.short_description = _('parents')
#
#     def labs(self, inst):
#         return u'<a href="{0}">{1}</a>'.format(
#             reverse('admin:labs_lab_change', args=[inst.lab.id]),
#             inst.lab.__unicode__())
#
#     labs.allow_tags = True
#     labs.short_description = _('lab')
#
#
# site.register(Unit, UnitAdmin)
#
#
