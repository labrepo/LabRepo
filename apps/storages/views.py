# -*- coding: utf-8 -*-
from django.views.generic import DetailView
from common.mixins import ActiveTabMixin, LoginRequiredMixin, CheckViewPermissionMixin, CheckLabPermissionMixin

from labs.models import Lab
from storages.forms import LabStorageForm


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


