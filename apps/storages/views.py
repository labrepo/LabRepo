# -*- coding: utf-8 -*-
import os

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse
from django.conf import settings
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView, RedirectView, FormView
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.db.models import Q

from common.mixins import (ActiveTabMixin, LoginRequiredMixin, CheckEditPermissionMixin, CheckViewPermissionMixin,
                           CheckDeletePermissionMixin, InviteFormMixin, CheckLabPermissionMixin, AjaxableResponseMixin)
from filemanager.views import check_directory
from labs.models import Lab
from storages.models import LabStorage
from storages.forms import LabStorageForm
from fabfile import create_test_lab


# class LabStorageCreate(AjaxableResponseMixin, CheckLabPermissionMixin, CreateView):
#     """
#     Create storage and add it to a lab instance
#     """
#     model = LabStorage
#     form_class = LabStorageForm
#
#     def get_success_url(self):
#         return reverse('labs:detail', args=(self.lab.pk,))
#
#     def form_valid(self, form):
#         lab_storage = form.save(commit=False)
#         lab_storage.lab = self.lab
#         lab_storage.save()
#         return HttpResponseRedirect(self.get_success_url())
#
#
# class LabStorageUpdate(AjaxableResponseMixin, CheckLabPermissionMixin, UpdateView):
#     """
#     Edit lab's storage.
#     """
#     model = LabStorage
#     form_class = LabStorageForm
#
#     def get_success_url(self):
#         return reverse('labs:detail', args=(self.lab.pk,))
#
#     def get(self, request, *args, **kwargs):
#         """
#         AJAX view. Return html with lab's storage form
#         """
#         form = self.form_class(instance=self.get_object())
#         csrf_token_value = request.COOKIES['csrftoken']
#         form_html = render_to_string('labs/storage_form.html', {
#             'form': form,
#             'storage': self.get_object(),
#             'lab': self.lab,
#             'csrf_token_value': csrf_token_value,
#         })
#         return self.render_to_json_response({'form_html': form_html})
#
#     def form_valid(self, form):
#         lab_storage = form.save()
#         return HttpResponseRedirect(self.get_success_url())
#
#
# class LabStorageDelete(AjaxableResponseMixin, CheckLabPermissionMixin, DeleteView):
#     """
#     AJAX view. Delete lab's storage.
#     """
#     model = LabStorage
#     form_class = LabStorageForm
#
#     def delete(self, request, *args, **kwargs):
#         lab_storage = self.get_object()
#         self.lab.storages.remove(lab_storage)
#         self.lab.save()
#         lab_storage.delete()
#         return self.render_to_json_response({'status': 'ok'})


class LabStorageIndex(LoginRequiredMixin, CheckViewPermissionMixin, ActiveTabMixin, DetailView):
    """
    View for display information about an existing laboratory with related experiments
    """
    model = Lab
    template_name = 'storages/index.html'
    active_tab = 'storages'
    pk_url_kwarg = 'lab_pk'

    def get_context_data(self, **kwargs):
        context = super(LabStorageIndex, self).get_context_data(**kwargs)
        context['active_tab'] = self.active_tab
        context['storage_form'] = LabStorageForm(scope_prefix='storage')

        return context


