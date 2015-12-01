# from django.core.urlresolvers import reverse
# from django.utils.translation import gettext_lazy as _
#
# from mongoadmin import site
# from common.admin import DocumentAdmin
# from common.filters import MongoRelatedFieldListFilter
# from .models import Experiment
#
#
# class ExperimentAdmin(DocumentAdmin):
#     list_filter = ('status', ('lab', MongoRelatedFieldListFilter),)
#     list_display = ('lab', 'title', 'owner', 'editor', 'viewer', 'start', 'end', 'status')
#     list_display_links = ('title',)
#
#     def owner(self, inst):
#         return ', '.join(['<a href="{0}">{1}</a>'.format(
#             reverse('admin:django_user_change', args=[user.id]),
#             user) for user in inst.owners])
#
#     owner.allow_tags = True
#     owner.short_description = _('owners')
#
#     def editor(self, inst):
#         return ', '.join(['<a href="{0}">{1}</a>'.format(
#             reverse('admin:django_user_change', args=[user.id]),
#             user) for user in inst.editors])
#
#     editor.allow_tags = True
#     editor.short_description = _('editors')
#
#     def viewer(self, inst):
#         return ', '.join(['<a href="{0}">{1}</a>'.format(
#             reverse('admin:django_user_change', args=[user.id]),
#             user) for user in inst.viewers])
#
#     viewer.allow_tags = True
#     viewer.short_description = _('viewers')
#
#
# site.register(Experiment, ExperimentAdmin)
