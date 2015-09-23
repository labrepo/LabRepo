# -*- coding: utf-8 -*-
import os

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse
from django.conf import settings
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView, RedirectView, FormView
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from mongoengine import Q

from common.mixins import (ActiveTabMixin, LoginRequiredMixin, CheckEditPermissionMixin, CheckViewPermissionMixin,
                           CheckDeletePermissionMixin, InviteFormMixin, CheckLabPermissionMixin, AjaxableResponseMixin)
from filemanager.views import check_directory
# from mongodbforms import embeddedformset_factory, EmbeddedDocumentForm
from mongodbforms import CharField, embeddedformset_factory, EmbeddedDocumentFormSet, EmbeddedDocumentForm
from labs.documents import Lab, LabStorage
from labs.forms import LabForm, LabStorageForm
from fabfile import create_test_lab

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
        self.object = form.save(commit=False)
        if not self.request.user in self.object.investigator:
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

        context['storage_form'] = LabStorageForm()

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
    model = Lab
    url = reverse_lazy('labs:list')

    def get(self, request, *args, **kwargs):
        self.request.user.create_test_lab()
        return super(BaseLabCreateView, self).get(request, *args, **kwargs)


class LabStorageCreate(AjaxableResponseMixin, CheckLabPermissionMixin, CreateView):
    model = LabStorage
    form_class = LabStorageForm

    def form_valid(self, form):
        lab_storage = form.save(commit=False)
        lab_storage.save()
        self.lab.storages.append(lab_storage)
        self.lab.save()

        return self.render_to_json_response({'status': 'ok', 'pk': u'{}'.format(lab_storage.pk)})


class LabStorageUpdate(AjaxableResponseMixin, CheckLabPermissionMixin, UpdateView):
    model = LabStorage
    form_class = LabStorageForm

    def get(self, request, *args, **kwargs):
        form = self.form_class(instance=self.get_object())

        form_html = render_to_string('labs/storage_form.html', {
            'form': form,
            'storage': self.get_object(),
            'lab': self.lab,
        })
        return self.render_to_json_response({'form_html': form_html})

    def form_valid(self, form):
        lab_storage = form.save()
        return self.render_to_json_response({'status': 'ok', 'pk': u'{}'.format(lab_storage.pk)})


class LabStorageDelete(AjaxableResponseMixin, CheckLabPermissionMixin, DeleteView):
    model = LabStorage
    form_class = LabStorageForm

    def delete(self, request, *args, **kwargs):
        lab_storage = self.get_object()
        self.lab.storages.remove(lab_storage)
        self.lab.save()
        lab_storage.delete()
        return self.render_to_json_response({'status': 'ok'})