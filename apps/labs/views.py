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
from labs.forms import LabForm


class LabCreateView(LoginRequiredMixin, InviteFormMixin, ActiveTabMixin, CreateView):
    """
     View for creating a new laboratory
    """
    model = Lab
    form_class = LabForm
    template_name = 'labs/lab_form.html'
    active_tab = 'labs'

    def form_valid(self, form):
        """
        If form is valid save create a new laboratory, if created user not in owners, add him there

        :param form: :class:`labs.forms.LabForm` instance
        :return: redirect to laboratories list
        """
        self.object = form.save()           # todo (commit=False)
        if not self.request.user in self.object.investigator.all():
            self.object.investigator.append(self.request.user)
        self.object.save()
        check_directory(os.path.join(settings.FILEMANAGER_UPLOAD_ROOT, unicode(self.object.id) + '/'))
        self.get_success_message()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('labs:list')

    def get_success_message(self):
        return messages.add_message(self.request, messages.SUCCESS, _('Lab was added successfully.'))

    def get_initial(self):
        return {'user': self.request.user}


class LabUpdateView(LoginRequiredMixin, InviteFormMixin, CheckEditPermissionMixin, ActiveTabMixin, UpdateView):
    """
     View for updating an existing laboratory
    """
    model = Lab
    form_class = LabForm
    template_name = 'labs/lab_form.html'
    active_tab = 'labs'
    pk_url_kwarg = 'lab_pk'

    def form_valid(self, form):
        """
        If form is valid save create a new laboratory, if created user not in owners, add him there

        :param form: :class:`labs.forms.LabForm` instance
        :return: redirect to laboratories list
        """
        response = super(LabUpdateView, self).form_valid(form)
        self.get_success_message()
        return response

    def get_success_message(self):
        return messages.add_message(self.request, messages.SUCCESS, _('Lab was updated successfully.'))

    def get_initial(self):
        return {'user': self.request.user}


class LabDeleteView(LoginRequiredMixin, CheckDeletePermissionMixin, ActiveTabMixin, DeleteView):
    """
     View for removing an existing laboratory
    """
    model = Lab
    success_url = reverse_lazy('labs:list')
    active_tab = 'labs'
    pk_url_kwarg = 'lab_pk'

    def delete(self, request, *args, **kwargs):
        response = super(LabDeleteView, self).delete(request, *args, **kwargs)
        self.get_success_message()
        return response

    def get_success_message(self):
        return messages.add_message(self.request, messages.SUCCESS, _('Lab was removed successfully.'))


class LabDetailView(LoginRequiredMixin, CheckViewPermissionMixin, ActiveTabMixin, DetailView):
    """
    View for display information about an existing laboratory with related experiments
    """
    model = Lab
    template_name = 'labs/lab_detail.html'
    active_tab = 'labs'
    pk_url_kwarg = 'lab_pk'

    def get_context_data(self, **kwargs):
        context = super(LabDetailView, self).get_context_data(**kwargs)
        return context


class LabListView(LoginRequiredMixin, ActiveTabMixin, ListView):
    """
     View for display laboratories list
    """
    model = Lab
    template_name = 'labs/lab_list.html'
    active_tab = 'labs'
    pk_url_kwarg = 'lab_pk'

    def get_context_data(self, **kwargs):
        ctx = super(LabListView, self).get_context_data(**kwargs)
        queryset = super(LabListView, self).get_queryset()
        ctx['active_tab'] = self.active_tab
        return ctx

    def get_queryset(self):
        """
        Display laboratories where user is assistant
        """
        queryset = super(LabListView, self).get_queryset()
        user = self.request.user
        queryset = queryset.filter(Q(members=user) | Q(guests=user) | Q(investigator=user))
        return queryset


class BaseLabCreateView(LoginRequiredMixin, RedirectView):
    """
    Create test lab
    """
    model = Lab
    url = reverse_lazy('labs:list')

    def get(self, request, *args, **kwargs):
        self.request.user.create_test_lab()
        return super(BaseLabCreateView, self).get(request, *args, **kwargs)