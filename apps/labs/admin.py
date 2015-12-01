# from django.core.urlresolvers import reverse
# from django.utils.translation import gettext_lazy as _
#
# from mongoadmin import site
# from labs.models import Lab
# from labs.forms import LabAdminForm
# from common.admin import DocumentAdmin
#
#
# class LabAdmin(DocumentAdmin):
#     form = LabAdminForm
#     list_display = ('name', 'investigators', 'member', 'guest')
#
#     def investigators(self, inst):
#         return u', '.join([u'<a href="{0}">{1}</a>'.format(
#             reverse('admin:django_user_change', args=[user.id]),
#             user.full_name) for user in inst.investigator])
#
#     investigators.allow_tags = True
#     investigators.short_description = _('investigators')
#
#     def member(self, inst):
#         return u', '.join([u'<a href="{0}">{1}</a>'.format(
#             reverse('admin:django_user_change', args=[user.id]),
#             user.full_name) for user in inst.members])
#
#     member.allow_tags = True
#     member.short_description = _('members')
#
#     def guest(self, inst):
#         return u', '.join([u'<a href="{0}">{1}</a>'.format(
#             reverse('admin:django_user_change', args=[user.id]),
#             user.full_name) for user in inst.guests])
#
#     guest.allow_tags = True
#     guest.short_description = _('viewers')
#
#
# site.register(Lab, LabAdmin)
