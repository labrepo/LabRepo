# -*- coding: utf-8 -*-
from __future__ import division
import random
import json

import numpy as np
import bokeh.plotting as bk
from bokeh.embed import autoload_static
from bokeh.resources import Resources

from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, View
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import ModelFormMixin, ProcessFormView

from common.decorators import get_obj_or_404
from dashboard.documents import RecentActivity
from measurements.documents import MeasurementType
from unit_collections.documents import Collection
from unit_collections.forms import UpdateUnitsCollectionForm
from common.mixins import LoginRequiredMixin, AjaxableResponseMixin, RecentActivityMixin, CheckLabPermissionMixin, \
    ActiveTabMixin, LabQueryMixin, JsTreeMixin
from unit_collections.mixins import CollectionPermissionMixin
from units.documents import Unit


class CollectionCreateView(LoginRequiredMixin, CollectionPermissionMixin, CreateView):

    def get_success_message(self):
        return ugettext(u'Collection was added successfully.')

    def form_valid(self, form):
        super(CollectionCreateView, self).form_valid(form)
        form = UpdateUnitsCollectionForm(initial={'lab': self.lab, 'user': self.request.user})
        return self.render_to_json_response({
            'message': self.get_success_message(),
            'update_collection_form': render_to_string('search/collection_form.html', {'update_collection_form': form}),
            'node': self.get_jstree_data([self.object], self.fields, self.parent_id)
        })


class CollectionUpdateView(LoginRequiredMixin, CollectionPermissionMixin, UpdateView):

    def get_success_message(self):
        return ugettext(u'Collection was changed successfully.')

    def get_context_data(self, **kwargs):
        context = super(CollectionUpdateView, self).get_context_data(**kwargs)
        context['measurement_types'] = set([measurement.measurement_type
                                           for unit in Unit.objects.filter(pk__in=[unit.pk for unit in self.object.units])
                                           for measurement in unit.measurements])
        return context


class CollectionUpdateUnitView(LoginRequiredMixin, CollectionPermissionMixin, SingleObjectTemplateResponseMixin,
                               ModelFormMixin, ProcessFormView, View):
    model = Collection
    form_class = UpdateUnitsCollectionForm
    template_name = 'unit_collections/unit_collections_form.html'

    def get(self, request, *args, **kwargs):
        self.object = None
        return super(CollectionUpdateUnitView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        return super(CollectionUpdateUnitView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.cleaned_data['collection']
        self.object.update(add_to_set__units=form.cleaned_data['units'])
        self.save_recent_activity(RecentActivity.UPDATE)
        self.get_success_message()
        return self.render_to_json_response({'message': self.get_success_message()})

    def get_success_message(self):
        return ugettext(u'Collection was changed successfully.')


class CollectionDeleteView(LoginRequiredMixin, CheckLabPermissionMixin, ActiveTabMixin, AjaxableResponseMixin,
                           RecentActivityMixin, DeleteView):
    """
    View for removing an existing unit collection
    """
    model = Collection
    template_name = 'unit_collections/unit_collections_form.html'
    active_tab = 'collections'

    def delete(self, request, *args, **kwargs):
        ids = request.POST.getlist('ids[]')
        object_list = self.model.objects.filter(lab=self.kwargs.get('lab_pk'), pk__in=ids)
        for obj in object_list:
            if not obj.is_owner(self.request.user):
                return self.render_to_json_response({'message': self.get_error_message()})
            self.save_recent_activity(RecentActivity.DELETE, obj=obj)
        object_list.delete()
        return self.render_to_json_response({'message': self.get_success_message()})

    def get_success_url(self):
        return reverse('collections:list', kwargs={'lab_pk': self.kwargs.get('lab_pk')})

    def get_success_message(self):
        return ugettext(u'Collection was removed successfully.')

    def get_error_message(self):
        return ugettext(u'You don\'t have permission to remove collection')


class CollectionListView(LoginRequiredMixin, CheckLabPermissionMixin, LabQueryMixin, JsTreeMixin, ActiveTabMixin, ListView):
    """
    View for display list of existing unit collections
    """
    model = Collection
    template_name = 'unit_collections/unit_collections_list.html'
    active_tab = 'collections'

    def get_queryset(self):
        queryset = super(CollectionListView, self).get_queryset()
        user = self.request.user
        collections = []
        if not self.lab.is_owner(user):
            for collection in queryset:
                if collection.is_assistant(user):
                    collections.append(collection.pk)
            return queryset.filter(pk__in=collections)
        return queryset

    def get_context_data(self, **kwargs):
        ctx = super(CollectionListView, self).get_context_data(**kwargs)
        ctx['collections'] = json.dumps(self.get_tree_element(self.model))
        return ctx

    def get_tree_element(self, model, fields=('id', 'title', 'title'), parent_id='#'):
        return self.get_jstree_data(self.get_queryset(), fields, parent_id=parent_id)


class PlotView(AjaxableResponseMixin, View):

    @method_decorator(get_obj_or_404)
    def get(self, request, *args, **kwargs):
        measurement_type_pk = kwargs.get('measurement_type_pk')
        measurement_type = MeasurementType.objects.get(pk=measurement_type_pk)
        collection = Collection.objects.get(pk=kwargs.get('pk'))
        units = Unit.objects.filter(measurements__match={'measurement_type': measurement_type.pk, 'active': True},
                                    pk__in=[unit.pk for unit in collection.units], active=True)
        if units:
            bk.hold()
            bk.figure(x_axis_type="datetime", tools="pan,wheel_zoom,box_zoom,reset,previewsave")
            colors = self.get_colors(len(units))

            for i, unit in enumerate(units):
                measurements = [(measurement.created_at, measurement.value) for measurement in unit.measurements
                                if measurement.active and measurement.measurement_type == measurement_type]

                measurements.sort(key=lambda measurement: measurement[0])
                data = {
                    'date': [measurement[0] for measurement in measurements],
                    'value': [measurement[1] for measurement in measurements]
                }
                bk.line(np.array(data['date']), data['value'], color=colors[i], line_width=2, legend=unit.__unicode__())

            bk.grid().grid_line_alpha = 0.3
            xax, yax = bk.axis()
            xax.axis_label = ugettext('Date')
            yax.axis_label = ugettext('Values')

            plot = bk.curplot()

            bk.get_default_color()

            plot.title = ugettext('Measurements type {}'.format(measurement_type.__unicode__()))
            js, tag = autoload_static(plot, Resources(mode='server', root_url=settings.STATIC_URL), "")
            return self.render_to_json_response({'plot': u'{}<script>{}</script>'.format(tag, js)})
        return self.render_to_json_response(ugettext('Not found'), status=404)

    @staticmethod
    def get_colors(count):
        colors = [
            "#2ca02c", "#1f77b4", "#d62728", "#ff9896",
            "#ff7f0e", "#ffbb78", "#98df8a",
            "#9467bd", "#c5b0d5", "#8c564b", "#c49c94",
            "#e377c2", "#f7b6d2", "#7f7f7f",
            "#bcbd22", "#dbdb8d", "#17becf", "#9edae5"
        ]
        if count > len(colors):
            h, s, v = random.random() * 6, 0.5, 243.2
            for i in range(count - len(colors)):
                h += 3.708
                colors.append('#'+'%02x'*3 % ((v, v - v * s * abs(1 - h % 2), v - v * s) * 3)[int(5**int(h)/3 % 3):: int(int(h) % 2 + 1)][:3])
                if i % 5/4:
                    s += .1
                    v -= 51.2
        return colors[:count]
