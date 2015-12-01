# from django.contrib import messages
# from django.contrib.admin.options import IS_POPUP_VAR
# from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
# from django.contrib.admin.util import unquote
# from django.contrib.contenttypes.models import ContentType
# from django.core.exceptions import PermissionDenied
# from django.core.urlresolvers import reverse
# from django.http.response import Http404, HttpResponseRedirect
# from django.template.response import TemplateResponse, SimpleTemplateResponse
# from django.utils.encoding import force_text
# from django.utils.html import escape, escapejs
# from django.utils.text import capfirst
# from django.utils.translation import ugettext_lazy as _
#
# from mongoadmin import DocumentAdmin as MongoAdmin
#
#
# class DocumentAdmin(MongoAdmin):
#     change_form_template = 'admin/admin_change_form.html'
#
#     def history_view(self, request, object_id, extra_context=None):
#         "The 'history' admin view for this model."
#         from django.contrib.admin.models import LogEntry
#         # First check if the user can see this history.
#         model = self.model
#         try:
#             obj = model.objects.get(pk=object_id)
#         except model.DoesNotExist:
#             raise Http404
#
#         if not self.has_change_permission(request, obj):
#             raise PermissionDenied
#
#         # Then get the history for this object.
#         opts = model._meta
#         app_label = opts.app_label
#         action_list = LogEntry.objects.filter(
#             object_id=unquote(object_id),
#             content_type__id__exact=ContentType.objects.get_for_model(model).id
#         ).select_related().order_by('action_time')
#
#         context = {
#             'title': _('Change history: %s') % force_text(obj),
#             'action_list': action_list,
#             'module_name': capfirst(force_text(opts.verbose_name_plural)),
#             'object': obj,
#             'app_label': app_label,
#             'opts': opts,
#             'preserved_filters': self.get_preserved_filters(request),
#         }
#         context.update(extra_context or {})
#         return TemplateResponse(request, self.object_history_template or [
#             "admin/%s/%s/object_history.html" % (app_label, opts.model_name),
#             "admin/%s/object_history.html" % app_label,
#             "admin/object_history.html"
#         ], context, current_app=self.admin_site.name)
#
#     def response_add(self, request, obj, post_url_continue=None):
#         """
#         Determines the HttpResponse for the add_view stage.
#         """
#         opts = obj._meta
#         pk_value = obj.pk
#         preserved_filters = self.get_preserved_filters(request)
#
#         msg_dict = {'name': force_text(opts.verbose_name), 'obj': force_text(obj)}
#         # Here, we distinguish between different save types by checking for
#         # the presence of keys in request.POST.
#         if IS_POPUP_VAR in request.POST:
#             return SimpleTemplateResponse('admin/popup_response.html', {
#                 'pk_value': escape(pk_value),
#                 'obj': escapejs(obj)
#             })
#
#         elif "_continue" in request.POST:
#             msg = _('The %(name)s "%(obj)s" was added successfully. You may edit it again below.') % msg_dict
#             self.message_user(request, msg, messages.SUCCESS)
#             if post_url_continue is None:
#                 post_url_continue = reverse('admin:%s_%s_change' %
#                                             (opts.app_label, opts.model_name),
#                                             args=(pk_value,),
#                                             current_app=self.admin_site.name)
#             post_url_continue = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, post_url_continue)
#             return HttpResponseRedirect(post_url_continue)
#
#         elif "_addanother" in request.POST:
#             msg = _('The %(name)s "%(obj)s" was added successfully. You may add another %(name)s below.') % msg_dict
#             self.message_user(request, msg, messages.SUCCESS)
#             redirect_url = request.path
#             redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
#             return HttpResponseRedirect(redirect_url)
#
#         else:
#             msg = _('The %(name)s "%(obj)s" was added successfully.') % msg_dict
#             self.message_user(request, msg, messages.SUCCESS)
#             return self.response_post_save_add(request, obj)
