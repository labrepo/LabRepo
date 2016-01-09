# -*- coding: utf-8 -*-
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import BaseDetailView
from django.utils.translation import gettext_lazy as _, ugettext

from common.mixins import (ActiveTabMixin, LoginRequiredMixin, CheckViewPermissionMixin,
                           CheckEditPermissionMixin, InitialLabMixin)
from units.models import Unit


class MeasurementTemplateView(LoginRequiredMixin, CheckEditPermissionMixin,
                             TemplateResponseMixin, BaseDetailView, View):
    """
    Render a measurement table template
    """
    model = Unit
    pk_url_kwarg = 'unit_pk'
    active_tab = 'measurement'
    template_name = 'measurement/measurement_list.html'

    def get_context_data(self, **kwargs):
        ctx = {'active_tab': self.active_tab, 'object': self.object}
        user = self.request.user
        ctx.update(self.kwargs)
        ctx['is_member'] = self.object.is_member(user) or self.object.is_owner(user)
        return ctx