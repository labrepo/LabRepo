# -*- coding: utf-8 -*-
import json
from bson import ObjectId

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.views.generic import View, DeleteView, UpdateView, DetailView
from django.views.generic.edit import ModelFormMixin
from django.views.generic.list import BaseListView, MultipleObjectTemplateResponseMixin
from django.template import RequestContext
from django.template.loader import render_to_string

from mongoengine import Q

from common.decorators import get_obj_or_404
from common.mixins import (ActiveTabMixin, LoginRequiredMixin, AjaxableResponseMixin,
                           RecentActivityMixin, CheckViewPermissionMixin, CommentMixin, DataMixin, JsTreeMixin,
                           InitialLabMixin)
from common.serializer import JsonDocumentEncoder
from dashboard.documents import RecentActivity
from .documents import Unit
from experiments.documents import Experiment
from .forms import UnitForm, UnitUpdateForm, UnitDescriptionForm
from labs.documents import Lab
from measurements.documents import MeasurementType
from tags.documents import Tag
from unit_collections.documents import Collection


class UnitCreateView(LoginRequiredMixin, RecentActivityMixin, DataMixin, AjaxableResponseMixin,
                     JsTreeMixin, ModelFormMixin, MultipleObjectTemplateResponseMixin, BaseListView, View):
    """
     View for creating a new unit
    """
    model = Unit
    form_class = UnitForm
    update_form_class = UnitUpdateForm
    template_name = 'units/unit_list.html'
    active_tab = 'units'
    title = {
        'pk': 'pk', 'sample': 'sample', 'experiments_pk': 'experiments', 'parent_pk': 'parent', 'tags_pk': 'tags',
        'change reasons': 'comment'
    }
    title_fields = ['pk', 'sample', 'experiments', 'parent', 'tags', 'readonly']
    extra_title = ['change reasons', 'experiments_pk', 'parent_pk', 'tags_pk']
    headers = ['pk', ugettext('sample'), ugettext('experiments'), ugettext('parents'), ugettext('tags'), 'readonly',
               ugettext('change reasons'), 'experiments_pk', 'parent_pk', 'tags_pk']

    @method_decorator(get_obj_or_404)
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.lab = self.lab
        user = self.request.user
        if not (self.object.is_member(user) or self.object.is_owner(user)):
            return {'errors': {'non_field_error': 'Permission denied'}, 'success': False}
        self.object = self.object.save(user=self.request.user, revision_comment=form.cleaned_data.get('comment'))
        self.save_recent_activity(self.flag, unit=self.object.pk,
                                  experiment=[unicode(obj.pk) for obj in self.object.experiments])
        return {'pk': unicode(self.object.pk), 'success': True}

    @method_decorator(login_required)
    @method_decorator(get_obj_or_404)
    def dispatch(self, *args, **kwargs):
        self.lab = Lab.objects.get(pk=self.kwargs.get('lab_pk'))
        if not self.lab.is_assistant(self.request.user):
            raise PermissionDenied
        return super(UnitCreateView, self).dispatch(*args, **kwargs)

    def get_units(self):
        """
        Filter units depending on user's permission
        """
        self.user = self.request.user
        if self.kwargs.get('experiment_pk'):
            experiments = [self.kwargs.get('experiment_pk')]
        else:
            experiments = self.get_experiments().values_list('id')
        self.object_list = self.object_list.filter(lab=self.lab, experiments__in=experiments, active=True)
        queryset = []
        for unit in self.object_list:
            if unit.is_assistant(self.user):
                record = []
                for field in self.title_fields[:-1]:
                    if hasattr(unit, field):
                        record.append(getattr(unit, field, None))
                record.append(unit.is_member(self.user) or unit.is_owner(self.user))
                queryset.append(JsonDocumentEncoder(fields=self.title_fields,
                                                    extra_fields=self.extra_title).encode_object(record))
        return queryset

    def get_experiments(self):
        experiments = Experiment.objects.filter(lab=self.lab, active=True)
        if self.lab.is_guest(self.user):
            experiments = experiments.filter(Q(owners=self.user) | Q(editors=self.user) | Q(viewers=self.user))
        return experiments

    def get_context_data(self, **kwargs):
        ctx = {'active_tab': self.active_tab}
        units_list = self.get_units()
        ctx['data'] = json.dumps(units_list)
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
            {'editor': 'multi-select', 'selectOptions': [[unicode(e[0]), e[1]] for e in units],
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
        ctx['is_member'] = bool(filter(lambda x: x[self.headers.index('readonly')], units_list) or len(experiments))
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
                    self.object.save(user=self.request.user)
                    Collection.objects.update(pull__units=self.object)
                    self.save_recent_activity(RecentActivity.DELETE, unit=pk,
                                              experiment=[unicode(obj.pk) for obj in self.object.experiments])
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
        self.object.save(user=self.request.user)
        self.save_recent_activity(RecentActivity.DELETE, unit=pk,
                                  experiment=[unicode(obj.pk) for obj in self.object.experiments])
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
    form_class = UnitDescriptionForm
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
        self.object.save(user=self.request.user)
        self.save_recent_activity(RecentActivity.UPDATE, unit=self.object.pk, experiment=[unicode(obj.pk) for obj in self.object.experiments])
        self.get_success_message()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_message(self):
        return messages.add_message(self.request, messages.SUCCESS, _('Unit was updated successfully.'))

    def get_context_data(self, **kwargs):
        ctx = super(UnitDetailView, self).get_context_data(**kwargs)
        ctx['measurements'] = self.get_measurement()
        return ctx

    def get_measurement(self):
        return self.object.measurements
        # result = self.model._get_collection().aggregate([
        #     {'$unwind': "$measurements"},
        #     {'$match': {'$and': [{'measurements.active': True}, {'_id': ObjectId(self.kwargs.get('pk'))}]}},
        #     {'$group': {
        #         '_id': {
        #             'measurement_type': "$measurements.measurement_type"
        #         },
        #         'values': {'$push': {
        #             'date': {
        #                 'year': {'$year': '$measurements.created_at'},
        #                 'month': {'$month': '$measurements.created_at'},
        #                 'day': {'$dayOfMonth': '$measurements.created_at'},
        #                 'hour': {'$hour': '$measurements.created_at'},
        #                 'minute': {'$minute': '$measurements.created_at'}
        #             },
        #             'value': "$measurements.value",
        #             'pk': "$measurements._id"
        #         }}
        #     }},
        # ])
        # for row in result['result']:
        #     row['measurement_type'] = MeasurementType.objects.get(pk=row['_id']['measurement_type'])
        # if result['result']:
        #     result['result'][0]['active'] = True
        # return result['result']


class UnitDetailJSONView(LoginRequiredMixin, CheckViewPermissionMixin, InitialLabMixin, RecentActivityMixin, ActiveTabMixin,
                     CommentMixin,AjaxableResponseMixin, DetailView):
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

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not (self.object.is_member(request.user) or self.object.is_owner(request.user)):
            raise PermissionDenied

        ctx = {}
        ctx.update(self.kwargs)

        if self.object.measurements:
            measurements = self.object.measurements.as_table()
        else:
            measurements = [
                ['', ''], ['', '']
            ]
        # if self.object.measurements:
        #     ctx['revisions'] = json.dumps(list(self.object.measurements.revisions()))
        ctx['measurements'] = json.dumps(measurements, cls=JsonDocumentEncoder, )

        ctx['description'] = self.object.description

        ctx['tags'] = render_to_string('tabs/unit_tags.html', {'tags': self.object.tags})
        ctx['comments'] = render_to_string('tabs/unit_comments.html', self.get_context_data())

        return self.render_to_json_response(ctx)

    def get_context_data(self, **kwargs):
        ctx = super(UnitDetailJSONView, self).get_context_data(**kwargs)
        ctx['lab'] = self.lab
        ctx['measurements'] = self.object.measurements
        return ctx