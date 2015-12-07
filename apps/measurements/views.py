import json
import re
import datetime
from bson import ObjectId

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, DeleteView, View, UpdateView
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import ModelFormMixin
from django.views.generic.list import MultipleObjectMixin
from django.utils.translation import gettext_lazy as _, ugettext
from django.utils import formats

from common.mixins import (ActiveTabMixin, LoginRequiredMixin, CheckViewPermissionMixin,
                           CheckDeletePermissionMixin, RecentActivityMixin,
                           CommentMixin, LabQueryMixin, DataMixin, AjaxableResponseMixin, DeleteDataMixin,
                           CheckEditPermissionMixin, InitialLabMixin)


from dashboard.models import RecentActivity
from history.models import History
from labs.models import Lab
from units.models import Unit

from .models import Measurement
from .forms import MeasurementForm, MeasurementUpdateForm, MeasurementDescriptionForm


class MeasurementCreateView(LoginRequiredMixin, CheckEditPermissionMixin, AjaxableResponseMixin, RecentActivityMixin,
                            ModelFormMixin, TemplateResponseMixin, BaseDetailView, View):
    """
     View for creating a new measurement
    """
    model = Unit
    pk_url_kwarg = 'unit_pk'
    form_class = MeasurementForm
    update_form_class = MeasurementUpdateForm
    active_tab = 'measurement'
    title = {
        'pk': 'pk', 'created_at': 'created_at', 'measurement_type_pk': 'measurement_type', 'value': 'value',
        'change reasons': 'comment', 'data': 'data'
    }
    template_name = 'measurement/measurement_list.html'
    title_field = ['pk', 'created_at', 'measurement_type', 'value']
    extra_title = ['change reasons', 'measurement_type_pk', 'readonly']
    headers = ['pk', ugettext('created at'), ugettext('measurement type'), ugettext('value'), ugettext('change reasons'),
               'measurement_type_pk', 'readonly']

    def get_context_data(self, **kwargs):
        ctx = {'active_tab': self.active_tab, 'object': self.object}
        user = self.request.user
        ctx.update(self.kwargs)
        if self.object.measurement:
            measurements = self.object.measurement.as_table()
        else:
            measurements = [
                ['', ''], ['', '']
            ]
        # if self.object.measurement:
        #     ctx['revisions'] = self.object.measurement.revisions()
        # ctx['data'] = json.dumps(measurements, cls=JsonDocumentEncoder, fields=self.title_field, extra_fields=self.extra_title)
        # print ctx['data']
        # measurement_type = MeasurementType.objects.filter(lab=self.kwargs['lab_pk'], active=True).values_list('pk', 'measurement_type')
        ctx['column'] = json.dumps([
            {'editor': 'text', 'display': 'none'},
            {'editor': 'text', 'display': 'none'},
            # {'editor': 'datetime'},
            # {'editor': 'select2', 'selectOptions': [[unicode(e[0]), e[1]] for e in measurement_type],
            #  'allowInvalid': True, 'append_url': reverse('measurements:measurement_type_append', kwargs={'lab_pk': self.kwargs['lab_pk']})},
            # {}, {},
            # {'editor': 'text', 'display': 'none'},
            # {'editor': 'text', 'display': 'none', 'default_value': (self.object.is_member(user) or self.object.is_owner(user)) or '', 'readonly': True},
        ])
        ctx['title'] = json.dumps(dict(zip(self.title_field + self.extra_title, self.headers)))
        ctx['headers'] = json.dumps(self.headers)
        # ctx['extra_form'] = MeasurementTypeForm(lab_pk=self.kwargs['lab_pk'])
        ctx['is_member'] = self.object.is_member(user) or self.object.is_owner(user)
        return ctx

    def get_object(self, queryset=None):
        if self.kwargs.get('pk'):
            self.form = self.update_form_class
            self.flag = RecentActivity.UPDATE
        else:
            self.form = self.form_class
            self.flag = RecentActivity.ADD
        return super(BaseDetailView, self).get_object()

    # def is_changed(self, data):
    #     return True
    #
    # def post(self, request, *args, **kwargs):
    #
    #     self.lab = Lab.objects.get(pk=self.kwargs.get('lab_pk'))
    #     data_list = dict(self.request.POST.iterlists())
    #     table_data = [[None] * int(data_list['width'][0]) for x in xrange(int(data_list['length'][0]))]
    #     headers = [None] * int(data_list['width'][0])
    #
    #     for key in data_list.keys():
    #         if key.startswith("row-0"):
    #             index = int(re.search(r'row-0-col-(.+?)', key).group(1))
    #             headers[index] = data_list[key][0]
    #         elif key.startswith("row-"):
    #             row_index = int(re.search(r'row-(.+)-col-.+', key).group(1))
    #             col_index = int(re.search(r'row-.+-col-(.+?)', key).group(1))
    #             table_data[row_index][col_index] = data_list[key][0]
    #
    #     self.object = self.get_object()
    #     user = request.user
    #     if self.object and not (self.object.is_member(user) or self.object.is_owner(user)):
    #         return self.render_to_json_response({'errors': {'non_field_error': 'Permission denied'}, 'success': False})
    #     if self.object.measurements:
    #         # create history revision for measurement
    #         measurements = self.object.measurements
    #         if measurements.headers != headers or measurements.table_data != table_data[1:]:
    #             # if measurment table data changed
    #             measurement_old = Measurement.objects.get(pk=self.object.measurements.pk)
    #             measurement_old.headers = headers
    #             measurement_old.table_data = table_data[1:]
    #             measurement_old.save(user=self.request.user, revision_comment=u'update')
    #             revision = measurement_old.latest_revision
    #             self.object.update(set__measurements=measurement_old)
    #             response = {'success': True,
    #                         'revision_pk': str(revision.id),
    #                         'revision_timestamp': formats.date_format(revision.timestamp, 'DATETIME_FORMAT'),
    #                         'revision_url': reverse('measurements:measurement-revert', kwargs={'lab_pk': self.object.lab.pk, 'unit_pk': self.object.id, 'revision_pk': revision.pk}),
    #                         }
    #
    #         else:
    #             response = {'success': True, 'message': 'nothing has changed'}
    #     else:
    #         # create new measurement
    #         measurement = Measurement(table_data=table_data[1:], headers=headers).save(user=self.request.user)
    #         self.object.measurements = measurement
    #         self.object = self.object.save(user=self.request.user)
    #         revision = measurement.latest_revision
    #         response = {'success': True,
    #                     'revision_pk': str(revision.id),
    #                     'revision_timestamp': formats.date_format(revision.timestamp, 'DATETIME_FORMAT'),
    #                     'revision_url': reverse('measurements:measurement-revert', kwargs={'lab_pk': self.object.lab.pk, 'unit_pk': self.object.id, 'revision_pk': revision.pk}),
    #                     }
    #
    #     return self.render_to_json_response(response)

    # def form_valid(self, form):
    #     if not self.kwargs.get('pk'):
    #         measurement = Measurement(**form.cleaned_data).save(user=self.request.user, revision_comment=form.cleaned_data.get('comment'))
    #         self.object.measurements.append(measurement)
    #         self.object = self.object.save(user=self.request.user)
    #     else:
    #         measurement = Measurement(pk=self.kwargs.get('pk'), **form.cleaned_data)
    #         self.model.objects(pk=self.kwargs[self.pk_url_kwarg], measurements___id=ObjectId(self.kwargs.get('pk'))).update(set__measurements__S=measurement)
    #         # todo update measurement instance change
    #         measurement_old = Measurement.objects.get(pk=self.kwargs.get('pk'))
    #         for key, value in form.cleaned_data.iteritems():
    #             setattr(measurement_old, key, value)
    #         measurement_old.save(user=self.request.user, revision_comment=form.cleaned_data.get('comment'))
    #     self.save_recent_activity(self.flag, obj=measurement, unit=self.object.pk, experiment=[unicode(obj.pk) for obj in self.object.experiments])
    #     return {'pk': unicode(measurement.pk), 'success': True}


class MeasurementDeleteView(LoginRequiredMixin, AjaxableResponseMixin, CheckDeletePermissionMixin, ActiveTabMixin,
                            RecentActivityMixin, DeleteView):
    """
    View for removing an existing measurement
    """
    model = Unit
    active_tab = 'measurement'
    pk_url_kwarg = 'unit_pk'

    def get_success_url(self):
        return reverse('measurements:list', kwargs={'unit_pk': self.kwargs.get('unit_pk'), 'lab_pk': self.kwargs['lab_pk']})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        ids = self.request.POST.get('data', '').split(',')
        measurements = Measurement.objects.filter(pk__in=ids)
        self.model.objects(measurements___id__in=measurements.values_list('pk')).update(set__measurements__S__active=False)
        for measurement in measurements:
            self.save_recent_activity(RecentActivity.DELETE, obj=measurement, unit=self.object.pk, experiment=[unicode(obj.pk) for obj in self.object.experiments])
            measurement.active = False
            measurement.save(user=self.request.user)
        return self.render_to_json_response({'data': ids, 'success': True})


class MeasurementDeleteOneView(LoginRequiredMixin, CheckDeletePermissionMixin, ActiveTabMixin, RecentActivityMixin, DeleteView):
    """
    View for removing an existing measurement
    """
    model = Unit
    active_tab = 'measurement'
    pk_url_kwarg = 'unit_pk'

    def get_success_url(self):
        return reverse('measurements:list', kwargs={'unit_pk': self.kwargs.get('unit_pk'), 'lab_pk': self.kwargs['lab_pk']})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        measurement = Measurement.objects.get(pk=self.kwargs['pk'])
        self.model.objects(measurements___id=measurement.pk).update(set__measurements__S__active=False)
        self.save_recent_activity(RecentActivity.DELETE, obj=measurement, unit=self.object.pk, experiment=[unicode(obj.pk) for obj in self.object.experiments])
        self.get_success_message()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_message(self):
        return messages.add_message(self.request, messages.SUCCESS, _('Measurement was removed successfully.'))


class MeasurementDetailView(LoginRequiredMixin, CheckViewPermissionMixin, InitialLabMixin, CommentMixin, RecentActivityMixin, UpdateView):
    model = Measurement
    template_name = 'measurement/measurement_detail.html'
    form_class = MeasurementDescriptionForm

    def get_success_url(self):
        return reverse('measurements:detail', kwargs={'lab_pk': self.kwargs['lab_pk'],
                                                      'unit_pk': self.kwargs['unit_pk'], 'pk': self.object.pk})

    def post(self, request, *args, **kwargs):
        response = super(MeasurementDetailView, self).post(request, *args, **kwargs)
        if not (self.object.is_member(request.user) or self.object.is_owner(request.user)):
            raise PermissionDenied
        return response

    def get_context_data(self, **kwargs):
        ctx = super(MeasurementDetailView, self).get_context_data(**kwargs)
        ctx['unit'] = self.object.get_unit()
        return ctx

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save(user=self.request.user)
        Unit.objects(pk=self.kwargs['unit_pk'], measurements___id=ObjectId(self.kwargs.get('pk'))).update(set__measurements__S=self.object)
        unit = Unit.objects.get(pk=self.kwargs['unit_pk'])
        self.save_recent_activity(RecentActivity.UPDATE, obj=self.object, unit=unit.pk,
                                  experiment=[unicode(obj.pk) for obj in unit.experiments])
        self.get_success_message()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_message(self):
        return messages.add_message(self.request, messages.SUCCESS, _('Measurement was updated successfully.'))


# class MeasurementTypeCreateView(LoginRequiredMixin, DataMixin, AjaxableResponseMixin, LabQueryMixin,
#                                 InitialLabMixin, RecentActivityMixin, MultipleObjectMixin, CreateView):
#     """
#      View for creating a new measurement type
#     """
#     model = MeasurementType
#     form_class = MeasurementTypeForm
#     template_name = 'measurement/measurement_type_list.html'
#     active_tab = 'measurement types'
#     title = {
#         'pk': 'pk', 'description': 'description', 'units': 'units', 'measurement_type': 'measurement_type'
#     }
#     title_fields = ['pk', 'description', 'units', 'measurement_type']
#     headers = ['pk', ugettext('description'), ugettext('the units'), ugettext('measurement type')]
#
#     def get_context_data(self, **kwargs):
#         ctx = {'active_tab': self.active_tab}
#         ctx['data'] = json.dumps(self.get_queryset().filter(active=True).values_list(*self.title_fields), cls=JsonDocumentEncoder,
#                                  fields=self.title_fields)
#         ctx['column'] = json.dumps([{'editor': 'text', 'display': 'none'}, {}, {}, {}])
#         ctx['title'] = json.dumps(dict(zip(self.title_fields, self.headers)))
#         ctx['headers'] = json.dumps(self.headers)
#         ctx['is_member'] = True
#         return ctx
#
#
# class MeasurementTypeAppendView(LoginRequiredMixin, AjaxableResponseMixin, RecentActivityMixin, CreateView):
#     """
#      View for creating a new measurement type
#     """
#     model = MeasurementType
#     form_class = MeasurementTypeForm
#     template_name = 'measurement/measurement_type_list.html'
#
#     def get_form_kwargs(self):
#         kwargs = super(MeasurementTypeAppendView, self).get_form_kwargs()
#         kwargs['lab_pk'] = self.kwargs.get('lab_pk')
#         return kwargs
#
#     def form_valid(self, form):
#         self.object = form.save(commit=False)
#         self.object.lab = Lab.objects.get(pk=self.kwargs.get('lab_pk'))
#         self.object.save()
#         self.save_recent_activity(RecentActivity.ADD)
#         return self.render_data()
#
#     def get_success_url(self):
#         return reverse('measurements:measurement_type_list', kwargs={'lab_pk': self.kwargs.get('lab_pk')})
#
#
# class MeasurementTypeDeleteView(LoginRequiredMixin, DeleteDataMixin, AjaxableResponseMixin, ActiveTabMixin, RecentActivityMixin, DeleteView):
#     """
#     View for removing an existing measurement type
#     """
#     model = MeasurementType
#     active_tab = 'measurement types'
#
#     def get_success_url(self):
#         return reverse('measurements:measurement_type_list', kwargs={'lab_pk': self.kwargs.get('lab_pk')})
#

class MeasurementHistoryRevert(LoginRequiredMixin, AjaxableResponseMixin, DataMixin, View):
    """
    View for getting measurement revision data
    """

    def post(self, request, *args, **kwargs):
        user = request.user
        unit = Unit.objects.get(pk=self.kwargs.get('unit_pk'))
        if unit and not (unit.is_member(user) or unit.is_owner(user)):
            return self.render_to_json_response({'errors': {'non_field_error': 'Permission denied'}, 'success': False})

        revision_pk = kwargs.get('revision_pk', '')
        revision = History.objects.get(pk=revision_pk)

        return self.render_to_json_response({
            'success': True,
            'table_data': revision.instance_data.get('table_data', ''),
            'headers': revision.instance_data.get('headers', ''),
            })