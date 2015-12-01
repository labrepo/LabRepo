# from django.contrib.auth.admin import sensitive_post_parameters_m, csrf_protect_m, UserAdmin
# from django.conf import settings
# from django.contrib import admin
# from django.contrib.auth.forms import AdminPasswordChangeForm
# from django.contrib.auth.models import Group
# from django.contrib import messages
# from django.core.exceptions import PermissionDenied
# from django.http import HttpResponseRedirect, Http404
# from django.template.response import TemplateResponse
# from django.utils.html import escape
# from django.utils.translation import ugettext, ugettext_lazy as _
#
# from mongoadmin import site
# from mongoengine import DoesNotExist
# from mongoengine.django.auth import User
# from registration.models import RegistrationProfile
#
# from common.admin import DocumentAdmin
# from profiles.forms import ChangeUserForm, ProfileCreationForm
#
#
# class UserMongoAdmin(DocumentAdmin):
#     add_form_template = 'admin/auth/user/add_form.html'
#     change_user_password_template = None
#     fieldsets = (
#         (None, {'fields': ('email', 'password')}),
#         (_('Personal info'), {'fields': ('first_name', 'last_name')}),
#         (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',)}),
#         (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'password1', 'password2')}
#         ),
#     )
#     form = ChangeUserForm
#     add_form = ProfileCreationForm
#     change_password_form = AdminPasswordChangeForm
#     list_display = ('email', 'first_name', 'last_name', 'is_staff')
#     #list_filter = ('is_active', 'is_staff', 'is_superuser')
#     search_fields = ('first_name', 'last_name', 'email')
#     filter_horizontal = ()
#
#     def get_user_or_404(self, request, id):
#         qs = self.queryset(request)
#         try:
#             user = qs.filter(pk=id)[0]
#         except (IndexError, DoesNotExist):
#             raise Http404
#         return user
#
#     def get_fieldsets(self, request, obj=None):
#         if not obj:
#             return self.add_fieldsets
#         return super(UserMongoAdmin, self).get_fieldsets(request, obj)
#
#     def get_form(self, request, obj=None, **kwargs):
#         """
#         Use special form during user creation
#         """
#         defaults = {}
#         if obj is None:
#             defaults['form'] = self.add_form
#         defaults.update(kwargs)
#         return super(UserMongoAdmin, self).get_form(request, obj, **defaults)
#
#     def get_urls(self):
#         from django.conf.urls import patterns
#         return patterns('',
#             (r'^([0-9a-f]{24})/password/$',
#              self.admin_site.admin_view(self.user_change_password))
#         ) + super(UserMongoAdmin, self).get_urls()
#
#     def lookup_allowed(self, lookup, value):
#         # See #20078: we don't want to allow any lookups involving passwords.
#         if lookup.startswith('password'):
#             return False
#         return super(UserMongoAdmin, self).lookup_allowed(lookup, value)
#
#     @sensitive_post_parameters_m
#     @csrf_protect_m
#     def add_view(self, request, form_url='', extra_context=None):
#         # It's an error for a user to have add permission but NOT change
#         # permission for users. If we allowed such users to add users, they
#         # could create superusers, which would mean they would essentially have
#         # the permission to change users. To avoid the problem entirely, we
#         # disallow users from adding users if they don't have change
#         # permission.
#         if not self.has_change_permission(request):
#             if self.has_add_permission(request) and settings.DEBUG:
#                 # Raise Http404 in debug mode so that the user gets a helpful
#                 # error message.
#                 raise Http404(
#                     'Your user does not have the "Change user" permission. In '
#                     'order to add users, Django requires that your user '
#                     'account have both the "Add user" and "Change user" '
#                     'permissions set.')
#             raise PermissionDenied
#         if extra_context is None:
#             extra_context = {}
#         username_field = self.model._meta.get_field(self.model.USERNAME_FIELD)
#         defaults = {
#             'auto_populated_fields': (),
#             'username_help_text': username_field.help_text,
#         }
#         extra_context.update(defaults)
#         return super(UserMongoAdmin, self).add_view(request, form_url,
#                                                extra_context)
#
#     @sensitive_post_parameters_m
#     def user_change_password(self, request, id, form_url=''):
#         if not self.has_change_permission(request):
#             raise PermissionDenied
#         user = self.get_user_or_404(request, id)
#         if request.method == 'POST':
#             form = self.change_password_form(user, request.POST)
#             if form.is_valid():
#                 form.save()
#                 msg = ugettext('Password changed successfully.')
#                 messages.success(request, msg)
#                 return HttpResponseRedirect('..')
#         else:
#             form = self.change_password_form(user)
#
#         fieldsets = [(None, {'fields': list(form.base_fields)})]
#         adminForm = admin.helpers.AdminForm(form, fieldsets, {})
#
#         context = {
#             'title': _('Change password: %s') % escape(getattr(user, user.USERNAME_FIELD)),#user.get_username()),
#             'adminForm': adminForm,
#             'form_url': form_url,
#             'form': form,
#             'is_popup': '_popup' in request.REQUEST,
#             'add': True,
#             'change': False,
#             'has_delete_permission': False,
#             'has_change_permission': True,
#             'has_absolute_url': False,
#             'opts': self.model._meta,
#             'original': user,
#             'save_as': False,
#             'show_save': True,
#         }
#         return TemplateResponse(request,
#             self.change_user_password_template or
#             'admin/auth/user/change_password.html',
#             context, current_app=self.admin_site.name)
#
#     def response_add(self, request, obj, post_url_continue=None):
#         """
#         Determines the HttpResponse for the add_view stage. It mostly defers to
#         its superclass implementation but is customized because the User model
#         has a slightly different workflow.
#         """
#         # We should allow further modification of the user just added i.e. the
#         # 'Save' button should behave like the 'Save and continue editing'
#         # button except in two scenarios:
#         # * The user has pressed the 'Save and add another' button
#         # * We are adding a user in a popup
#         if '_addanother' not in request.POST and '_popup' not in request.POST:
#             request.POST['_continue'] = 1
#         return super(UserMongoAdmin, self).response_add(request, obj, post_url_continue)
#
#
# admin.site.unregister(RegistrationProfile)
# admin.site.unregister(Group)
# site.register(User, UserMongoAdmin)
