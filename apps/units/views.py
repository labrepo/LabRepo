# -*- coding: utf-8 -*-
import json
import logging

import bs4
import requests
from urlparse import urlparse

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.views.generic import View, DeleteView, UpdateView, DetailView
from django.views.generic.edit import ModelFormMixin
from django.views.generic.list import BaseListView, MultipleObjectTemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import formats
from django.core import serializers

from preserialize.serialize import serialize  # todo change with drf serizlizer

from django.db.models import Q

from common.decorators import get_obj_or_404
from common.mixins import (ActiveTabMixin, LoginRequiredMixin, AjaxableResponseMixin,
                           RecentActivityMixin, CheckViewPermissionMixin, CommentMixin, DataMixin, JsTreeMixin,
                           InitialLabMixin)
# from common.serializer import JsonDocumentEncoder
from uploader.views import FileUploadMixinView, DropboxFileUploadMixinView, LocalFileUploadMixinView
from dashboard.models import RecentActivity
from .models import Unit, UnitFile, UnitLink
from experiments.models import Experiment
from .forms import UnitForm
from labs.models import Lab
from tags.models import Tag
# from unit_collections.models import Collection

logger = logging.getLogger(__name__)


class UnitTableView(LoginRequiredMixin, RecentActivityMixin, JsTreeMixin,
                     ModelFormMixin, MultipleObjectTemplateResponseMixin, BaseListView, View):
    """
    Render a unit table template
    """
    model = Unit
    template_name = 'units/unit_list.html'
    active_tab = 'units'
    title = {
        'pk': 'pk', 'sample': 'sample', 'experiments_pk': 'experiments', 'parent_pk': 'parent', 'tags_pk': 'tags',
        'change reasons': 'comment',
    }
    title_fields = ['pk', 'sample', 'experiments', 'parent', 'tags', 'readonly']
    extra_title = ['change reasons', 'experiments_pk', 'parent_pk', 'tags_pk']
    headers = ['pk', ugettext('sample'), ugettext('experiments'), ugettext('parents'), ugettext('tags'), 'readonly',
               ugettext('change reasons'), 'experiments_pk', 'parent_pk', 'tags_pk']


    @method_decorator(login_required)
    @method_decorator(get_obj_or_404)
    def dispatch(self, *args, **kwargs):
        self.user = self.request.user
        self.lab = Lab.objects.get(pk=self.kwargs.get('lab_pk'))
        if not self.lab.is_assistant(self.request.user):
            raise PermissionDenied
        return super(UnitTableView, self).dispatch(*args, **kwargs)

    def get_experiments(self):
        experiments = Experiment.objects.filter(lab=self.lab, active=True)
        if self.lab.is_guest(self.user):
            experiments = experiments.filter(Q(owners=self.user) | Q(editors=self.user) | Q(viewers=self.user))
        return experiments

    def get_context_data(self, **kwargs):
        ctx = {'active_tab': self.active_tab}
        lab = self.kwargs['lab_pk']
        experiments = self.get_experiments().values_list('pk', 'title')
        if 'experiment_pk' in self.kwargs:
            ctx['experiment'] = Experiment.objects.get(pk=self.kwargs.get('experiment_pk'))
        units = Unit.objects.filter(lab=lab, active=True).values_list('pk', 'sample')
        tags = Tag.objects.filter(lab=lab)
        ctx['column'] = json.dumps([
            {'editor': 'text', 'display': 'none'},
            {},
            {
                'editor': 'multi-select', 'selectOptions': [[unicode(e[0]), e[1]] for e in experiments],
                # 'validator_string': u'|'.join([e[1] for e in experiments]), 'allowInvalid': True
            },
            {
                'editor': 'multi-select', 'selectOptions': [[unicode(e[0]), e[1]] for e in units],
                # 'validator_string': '[%s]*' % u'|'.join([e[1] for e in units]), 'allowInvalid': True
            },
            {'editor': 'jstree', 'selectOptions': self.get_jstree_data(tags), 'renderer': 'renderTags'},
            # {'editor': 'text'},
            {'editor': 'text', 'display': 'none', 'readonly': True},
            {'editor': 'text'},
            {'editor': 'text', 'display': 'none'},
            {'editor': 'text', 'display': 'none'},
            {'editor': 'text', 'display': 'none'},
        ])
        ctx['title'] = json.dumps(dict(zip(self.title_fields + self.extra_title, self.headers)))
        ctx['headers'] = json.dumps(self.headers)
        # ctx['is_member'] = bool(filter(lambda x: x[self.headers.index('readonly')], units_list) or len(experiments))
        ctx['is_member'] = bool(len(experiments))
        return ctx


class UnitDeleteView(LoginRequiredMixin, RecentActivityMixin, ActiveTabMixin, AjaxableResponseMixin, View):
    """
    View for removing an existing unit
    """
    model = Unit
    active_tab = 'units'

    def post(self, request, *args, **kwargs):
        ids = self.request.POST.get('data', '').split(',')
        removed = []
        for pk in ids:
            try:
                self.object = self.model.objects.get(pk=pk)
                if not self.object.is_owner(self.request.user):
                    removed.append({'errors': {'non_field_error': 'Permission denied'}, 'success': False})
                else:
                    self.object.active = False
                    # self.object.save(user=self.request.user)
                    self.object.save()
                    # Collection.objects.update(pull__units=self.object)
                    self.save_recent_activity(RecentActivity.DELETE, unit=pk,
                                              experiment=[unicode(obj.pk) for obj in self.object.experiments.all()])
                    removed.append(pk)
            except self.model.DoesNotExist:
                pass
        return self.render_to_json_response({'data': removed, 'success': True})


class UnitDeleteOneView(LoginRequiredMixin, RecentActivityMixin, ActiveTabMixin, DeleteView):
    """
    View for removing an existing unit
    """
    model = Unit
    active_tab = 'units'

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        self.object = self.model.objects.get(pk=pk)
        if not self.object.is_owner(self.request.user):
            raise PermissionDenied
        self.object.active = False
        self.object.save()
        # self.object.save(user=self.request.user)
        self.save_recent_activity(RecentActivity.DELETE, unit=pk,
                                  experiment=[unicode(obj.pk) for obj in self.object.experiments.all()])
        self.get_success_message()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('units:list', kwargs={'lab_pk': self.kwargs.get('lab_pk')})

    def get_success_message(self):
        return messages.add_message(self.request, messages.SUCCESS, _('Unit was removed successfully.'))


class UnitDetailView(LoginRequiredMixin, CheckViewPermissionMixin, InitialLabMixin, RecentActivityMixin, ActiveTabMixin,
                     CommentMixin, UpdateView):
    """
    View for display information about an existing unit
    """
    model = Unit
    form_class = UnitForm
    template_name = 'units/unit_detail.html'
    active_tab = 'units'

    def get_object(self, queryset=None):
        unit = super(UnitDetailView, self).get_object(queryset)
        if not unit.is_assistant(self.request.user):
            raise PermissionDenied
        return unit

    def post(self, request, *args, **kwargs):
        response = super(UnitDetailView, self).post(request, *args, **kwargs)
        if not (self.object.is_member(request.user) or self.object.is_owner(request.user)):
            raise PermissionDenied
        return response

    def form_valid(self, form):
        self.object = form.save(commit=False)
        # self.object.save(user=self.request.user)
        self.object.save()
        self.save_recent_activity(RecentActivity.UPDATE, unit=self.object.pk, experiment=[unicode(obj.pk) for obj in self.object.experiments.all()])
        self.get_success_message()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_message(self):
        return messages.add_message(self.request, messages.SUCCESS, _('Unit was updated successfully.'))

    def get_context_data(self, **kwargs):
        ctx = super(UnitDetailView, self).get_context_data(**kwargs)
        ctx['measurements'] = self.get_measurement()
        return ctx

    def get_measurement(self):
        return self.object.measurement


class UnitDetailJSONView(LoginRequiredMixin, CheckViewPermissionMixin, JsTreeMixin, InitialLabMixin,
                         RecentActivityMixin, ActiveTabMixin, CommentMixin, AjaxableResponseMixin, DetailView):
    """
    View for return json information about an existing unit(is used on experiment page)
    """
    model = Unit
    template_name = 'units/unit_detail.html'
    active_tab = 'units'

    def get_object(self, queryset=None, *args, **kwargs):
        unit = super(UnitDetailJSONView, self).get_object(queryset)
        return unit

    @method_decorator(login_required)
    @method_decorator(get_obj_or_404)
    def dispatch(self, *args, **kwargs):
        self.lab = Lab.objects.get(pk=self.kwargs.get('lab_pk'))
        if not self.lab.is_assistant(self.request.user):
            raise PermissionDenied
        return super(UnitDetailJSONView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not (self.object.is_member(request.user) or self.object.is_owner(request.user)):
            raise PermissionDenied

        context = self.get_context_data()
        ctx = {}
        ctx.update(self.kwargs)

        ctx['tags'] = json.dumps(self.get_tree_element(self.object))

        ctx['uploader'] = render_to_string('units/tabs/unit_uploader.html', context)
        ctx['comments'] = render_to_string('units/tabs/unit_comments.html', context)

        return self.render_to_json_response(ctx)

    def get_tree_element(self, object, fields=('id', 'parent', 'details'), parent_id='#'):
        tags = object.tags
        tags_tree = self.get_jstree_data(tags, fields, parent_id=parent_id)
        return tags_tree

    def get_context_data(self, **kwargs):
        ctx = super(UnitDetailJSONView, self).get_context_data(**kwargs)
        ctx['lab'] = self.lab
        ctx['lab_pk'] = self.lab.pk
        ctx['user'] = self.request.user
        return ctx


class UnitFileUploadView(FileUploadMixinView):
    model = UnitFile
    parent_model = Unit


class UnitFileDropboxUploadView(DropboxFileUploadMixinView):
    model = UnitFile
    parent_model = Unit


class UnitFileLocalUploadView(LocalFileUploadMixinView):
    model = UnitFile
    parent_model = Unit
